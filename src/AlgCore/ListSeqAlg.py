from AlgCore.AlgBase import AlgBase
import math
import functools
import copy


class ListSeqMethod(AlgBase):
    def __init__(self):
        self.EM = []  # 存放EM紧急任务
        self.FE = []  # 存放前台任务
        self.BE = []  # 存放BE任务
        self.driver_statues = []  # 存放驱动器信息
        self.ans = []  # 最终返回的json格式列表
        self.cur_clock = 0
        self.fe_punish_score = 0
        self.em_punish_score = 0
        self.praise_score = 0

    def get_score(self):
        return self.praise_score - self.fe_punish_score - self.em_punish_score

    def disp_list(self, alist):
        '''
        打印列表
        :param alist:
        :return:
        '''
        for ele in alist:
            print(ele)

    def op_task(self, logical_clock: int, request_list: list, driver_statues: list):
        '''
        基本的贪心思想，顺序地使用每个驱动器，一个的空间尽可能用完了再去装下一个，并且根据顺序EM->FE->BE尽可多地把任务装驱动器
        :param driver_statues: 驱动器信息
        :return: 当前时间刻的处理信息列表
        '''
        self.driver_statues = copy.deepcopy(driver_statues)  # 使用深拷贝
        self.ans = []  # 每个小时进入时清空一次
        for driver in self.driver_statues:
            # 初始化当前驱动器需要处理的json格式信息
            cur_exce_info = dict()
            cur_request_list = []
            cur_exce_info['DriverID'] = driver['DriverID']
            cur_exce_info['LogicalClock'] = self.cur_clock

            # 先处理EM
            ind = len(self.EM) - 1
            while ind >= 0:  # 后往前找，尽可能填满
                if self.EM[ind]['RequestSize'] < driver['Capacity'] and driver['DriverID'] in self.EM[ind]['Driver']:
                    # 计算分数
                    if self.cur_clock - self.EM[ind]['LogicalClock'] >= 1:
                        self.em_punish_score += 2 * (self.cur_clock - self.EM[ind]['LogicalClock']) * \
                                             math.ceil(self.EM[ind]['RequestSize']/50)
                    # 相关处理
                    cur_request_list.append(self.EM[ind]['RequestID'])
                    driver['Capacity'] -= self.EM[ind]['RequestSize']
                    self.EM.pop(ind)
                ind -= 1

            # 处理FE
            ind = len(self.FE) - 1
            while ind >= 0:  # 后往前找，尽可能填满
                if self.FE[ind]['RequestSize'] < driver['Capacity'] and driver['DriverID'] in self.FE[ind]['Driver']:
                    if self.cur_clock - self.FE[ind]['LogicalClock'] >= self.FE[ind]['SLA']:
                        self.fe_punish_score += (self.cur_clock - self.FE[ind]['LogicalClock']) * \
                                             math.ceil(self.FE[ind]['RequestSize']/50)
                    cur_request_list.append(self.FE[ind]['RequestID'])
                    driver['Capacity'] -= self.FE[ind]['RequestSize']
                    self.FE.pop(ind)
                ind -= 1

            # 处理BE
            ind = len(self.BE) - 1
            while ind >= 0:  # 后往前找，尽可能填满
                if self.BE[ind]['RequestSize'] < driver['Capacity'] and driver['DriverID'] in self.BE[ind]['Driver']:
                    if self.BE[ind]['RequestSize'] < driver['Capacity']:
                        if self.cur_clock - self.BE[ind]['LogicalClock'] <= 12:
                            self.praise_score += 0.5 * math.ceil(self.BE[ind]['RequestSize'] / 50)
                    cur_request_list.append(self.BE[ind]['RequestID'])
                    driver['Capacity'] -= self.BE[ind]['RequestSize']
                    self.BE.pop(ind)
                ind -= 1

            cur_exce_info['RequestList'] = cur_request_list
            self.ans.append(cur_exce_info)
        print(f'调度信息：')
        self.disp_list(self.ans)
        return self.ans

    def task_assign(self, logical_clock: int, request_list: list, driver_statues: list):
        '''
        对任务进行分类
        :param logical_clock:
        :param request_list:
        :return:
        '''
        self.cur_clock = logical_clock
        # 把已经超过时间的给丢弃掉
        self.delete_tle_task()
        # 根据类型分别把任务放到几个队列中
        for i in range(len(request_list)):
            if request_list[i]['RequestType'] == 'EM':
                self.EM.append(request_list[i])
            elif request_list[i]['RequestType'] == 'BE':
                self.BE.append(request_list[i])
            elif request_list[i]['RequestType'] == 'FE':
                self.FE.append(request_list[i])
                # if request_list[i]['SLA'] == 1:
                #     self.FE_1.append(request_list[i])
                # elif request_list[i]['SLA'] == 6:
                #     self.FE_6.append(request_list[i])
                # elif request_list[i]['SLA'] == 12:
                #     self.FE_12.append(request_list[i])
        # 根据任务优先级进行排序：FE根据时间要求降序、任务容量升序；BE根据任务容量升序；EM根据任务容量升序
        self.EM.sort(key=functools.cmp_to_key(cmp1))
        # print(f'EM列表完成排序，结果为:')
        # self.disp_list(self.EM)
        # print('-'*30)
        self.BE.sort(key=functools.cmp_to_key(cmp1))
        # print(f'BE列表完成排序，结果为：')
        # self.disp_list(self.BE)
        # print('-' * 30)
        self.FE.sort(key=functools.cmp_to_key(cmp2))
        # print(f'FE列表完成排序，结果为：')
        # self.disp_list(self.FE)
        # print('-' * 30)

    def delete_tle_task(self):
        '''
        丢弃已经超时的任务并扣分
        :return:
        '''
        length = len(self.EM)
        task_ind = length - 1
        while task_ind >= 0:
            if self.cur_clock - self.EM[task_ind]['SLA'] == 12:
                self.EM.pop(task_ind)
            task_ind -= 1

        length = len(self.FE)
        task_ind = length - 1
        while task_ind >= 0:
            if self.cur_clock - self.FE[task_ind]['SLA'] == 12:
                self.FE.pop(task_ind)
            task_ind -= 1

        # for task_ind in range(len(self.FE_1)):
        #     if self.cur_clock - self.FE_1[task_ind]['SLA'] == 12:
        #         self.punish_score += 12 * math.ceil(self.FE_1[task_ind]['RequestSize']/50)
        #         self.EM.pop(task_ind)
        #
        # for task_ind in range(len(self.FE_6)):
        #     if self.cur_clock - self.FE_6[task_ind]['SLA'] == 12:
        #         self.punish_score += 12 * math.ceil(self.FE_6[task_ind]['RequestSize']/50)
        #         self.EM.pop(task_ind)
        #
        # for task_ind in range(len(self.FE_12)):
        #     if self.cur_clock - self.FE_12[task_ind]['SLA'] == 12:
        #         self.punish_score += 12 * math.ceil(self.FE_12[task_ind]['RequestSize']/50)
        #         self.EM.pop(task_ind)
        length = len(self.BE)
        task_ind = length - 1
        while task_ind >= 0:
            if self.cur_clock - self.BE[task_ind]['SLA'] == 12:
                self.BE.pop(task_ind)
            task_ind -= 1


def cmp1(x, y):
    '''
    自定义比较函数
    :param x:
    :param y:
    :return:
    '''
    if x['RequestSize'] > y['RequestSize']:
        return 1
    return -1


def cmp2(x, y):
    '''
    自定义比较函数
    :param x:
    :param y:
    :return:
    '''
    if x['SLA'] < y['SLA']:
        return 1
    elif x['SLA'] == y['SLA'] and x['RequestSize'] > y['RequestSize']:
        return 1
    return -1