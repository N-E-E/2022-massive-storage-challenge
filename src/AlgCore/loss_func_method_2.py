from AlgCore.AlgBase import AlgBase
import score
import math
import copy
import logger


class LossFuncMethod2(AlgBase):
    def __init__(self):
        self.request = dict()  # 存储请求
        self.drivers = dict()  # 存储驱动器信息
        self.driver_return_info_dict = dict()  # 里面存储的是driver_id-json对，方便后面修改要返回的json信息
        self.cur_clock = 0
        self.ans = []  # 最终返回的json格式列表
        self.score = score.Score()
        self.rest_time_value_sum = 0  # 每个value的和，方便后续归一化，下同
        self.score_value_sum = 0
        self.logger = logger.LfLogger()

    def get_score(self) -> tuple[int, int, int, int]:
        """
        获取模拟分数
        """
        cur_score = self.score.get_detail_score()
        self.logger.print_detail_score(cur_score)
        return cur_score

    def find_best_driver(self, request_list):
        """
        1. 统计每个驱动器可以处理多少容量的任务，统计到两倍的最大容量为止\n
        2. 为每个请求找到最适合的驱动器\n
        要求传入的request_list已经按分数降序排序

        Args:
            request_list: 排序后的请求列表list[dict()]
        Returns:
            请求列表中最后不处理的那个请求id
        """
        max_handle_size = 0  # 记录当前这一轮最多打算处理多少容量的任务
        driver_size_sum = 0  # 记录驱动器capacity总和
        last_task = -1  # 记录最后一个任务(这个任务不处理).最后返回这个值
        # 统计driver_size_sum
        for driver_json in self.drivers.values():
            driver_size_sum += driver_json['Capacity']
        # 统计每个驱动器在这一轮可能处理的任务总容量
        for request_json in request_list:
            for driver_id in request_json['Driver']:
                self.drivers[driver_id]['TaskSize'] += request_json['RequestSize']
                max_handle_size += request_json['RequestSize']
                if max_handle_size > 2 * driver_size_sum:
                    last_task = request_json['RequestID']
                    break
        # 统计当前每条请求的驱动器选择列表
        for request_json in request_list:
            if request_json['RequestID'] == last_task:
                break
            # 可以用的驱动器的json列表
            avail_driver_json_list = [self.drivers[driver_id] for driver_id in request_json['Driver']]
            # 按照tasksize排序
            avail_driver_json_list.sort(key=lambda x: x['TaskSize']/x['Capacity'])  # 分母为0会寄，还没改
            # 提取每个json的id作为选择驱动器的顺序，存放到每条请求的json信息中
            balance_driver_list = [driver_json['DriverID'] for driver_json in avail_driver_json_list]
            request_json['balance_driver_seq'] = balance_driver_list
        return last_task


    def gen_value_1(self):
        """
        生成某条请求的分数。这是优化的核心

        Args:
            self
        Returns:
            None
        """
        # 计算此时距离丢弃还剩下多少时间并把所有分数相加方便后面归一化,下同.
        self.rest_time_value_sum = 0
        self.score_value_sum = 0
        for ID in self.request.keys():
            if self.request[ID] == 'BE':
                rest_time = max(0, self.request[ID]['SLA'] - (self.cur_clock - self.request[ID]['LogicalClock']))
            else:
                rest_time = max(0, self.request[ID]['SLA'] + 12 - (self.cur_clock - self.request[ID]['LogicalClock']))

            # 剩余时间越少越紧急，因此rest_time_value和rest_time是负相关，同时问了保证value为正要用12去减
            # 这就要求在计算value之前需要先把超时的丢弃掉，不然没意义
            #rest_time_value = 12 - rest_time
            self.request[ID]['rest_time_value'] = rest_time
            self.rest_time_value_sum += rest_time

        # 计算假设此时开始做任务的扣分/加分，扣分/加分越重value越大
        # 也要求先把已经超时的给丢弃掉
        for ID in self.request.keys():
            if self.request[ID]['RequestType'] == 'EM':
                score_value = 2 * max(0, self.cur_clock - self.request[ID]['LogicalClock'] - 1 + 1) * \
                                             math.ceil(self.request[ID]['RequestSize']/50)
            elif self.request[ID]['RequestType'] == 'FE':
                score_value = max(0, self.cur_clock - self.request[ID]['LogicalClock'] - self.request[ID]['SLA'] + 1) * \
                          math.ceil(self.request[ID]['RequestSize'] / 50)
            else:
                score_value = 0.5 * math.ceil(self.request[ID]['RequestSize'] / 50)
            self.request[ID]['score_value'] = score_value
            self.score_value_sum += score_value

        # 驱动器利用率：不知道这个分数怎么计算

        # 归一化后计算value
        for ID in list(self.request.keys()):
            # if self.rest_time_value_sum != 0:
            #     # +1防止出现为0的情况
            #     self.request[ID]['rest_time_value_final'] = self.request[ID]['rest_time_value'] + 1\
            #                                                 / self.rest_time_value_sum
            # else:
            #     self.request[ID]['rest_time_value_final'] = 1
            # if self.score_value_sum != 0:
            #     self.request[ID]['score_value_final'] = self.request[ID]['score_value'] / self.score_value_sum
            # else:
            #     self.request[ID]['score_value_final'] = 0
            self.request[ID]['value'] = self.request[ID]['rest_time_value']

    def delete_tle_task(self):
        """
        删除已经超时的任务并扣分

        Args:
            self
        Returns:
            None
        """
        key_list = copy.deepcopy(list(self.request.keys()))
        for k in key_list:
            if self.request[k]['RequestType'] == 'BE':
                if self.cur_clock - self.request[k]['LogicalClock'] == 12:
                    del self.request[k]
            elif self.cur_clock - self.request[k]['LogicalClock'] - self.request[k]['SLA'] == 12:
                self.score.mark(self.request[k], self.cur_clock)
                del self.request[k]

    def op_task(self, logical_clock: int, request_list: list, driver_statues: list) -> list:
        """
        对task_assign函数中预存储好的数据进行分配。思路是根据请求的value进行顺序处理，同时选择最好的驱动器进行处理

        Args:
            logical_clock: 当前时刻
            request_list: 请求列表
            driver_statues: 驱动器信息列表
        Returns:
            返回题目要求的json构成的列表
        """
        self.ans = []  # 每个小时进入时清空一次
        self.gen_value_1()  # 更新当前小时还未丢弃的请求的value
        sort_list = sorted(list(self.request.values()), key=lambda x: x['value'], reverse=False)
        # 为每条记录生成选择驱动器列表
        last_task = self.find_best_driver(sort_list)
        # 输出调试
        self.logger.disp_list(list(self.drivers.values()), '驱动器处理任务量信息：')
        self.logger.disp_list(list(self.request.values()), '平衡驱动器列表后的请求信息')
        for json in sort_list:
            if json['RequestID'] == last_task:
                break
            for avail_driver in json['balance_driver_seq']:
                if json['RequestSize'] <= self.drivers[avail_driver]['Capacity']:
                    self.driver_return_info_dict[avail_driver]['RequestList'].append(json['RequestID'])
                    self.driver_return_info_dict[avail_driver]['LogicalClock'] = self.cur_clock
                    # 更新剩余容量
                    self.drivers[avail_driver]['Capacity'] -= json['RequestSize']
                    # 计算分数然后删除这个请求
                    self.score.mark(json, self.cur_clock)
                    del self.request[json['RequestID']]
                    break
        self.ans = list(self.driver_return_info_dict.values())
        # 打印信息
        self.logger.disp_list(self.ans, '返回的json信息:')
        self.logger.print_use_rate(self.drivers)
        return self.ans

    def task_assign(self, logical_clock: int, request_list: list, driver_statues: list):
        """
        对请求任务/驱动器信息以dict形式存储，键为id

        Args:
            logical_clock:当前时刻
            request_list:请求列表
            driver_statues:驱动器信息列表
        Returns:
            None
        """
        self.cur_clock = logical_clock
        # 删除已经超时的任务
        self.delete_tle_task()
        # 把传入的两个json数组先保存下来(用字典存储)
        # 读取请求
        for json in request_list:
            self.request[json['RequestID']] = json
        # 读取驱动器
        for json in driver_statues:
            self.drivers[json['DriverID']] = json
            self.drivers[json['DriverID']]['TaskSize'] = 0
            # 初始化self.driver_return_info_dict
            self.driver_return_info_dict[json['DriverID']] = {'DriverID': json['DriverID'], 'RequestList': [],
                                                              'LogicalClock': -1}
        self.logger.store_origin_drivers_info(self.drivers)
