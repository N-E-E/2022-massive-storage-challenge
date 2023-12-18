"""
打印日志,可以选择输出到文件或屏幕。
推荐输出到文件
"""
import copy
from abc import ABCMeta, abstractmethod


class Logger:
    """
    抽象类，根据自己的算法写几个函数打印一下调试日志
    """
    @abstractmethod
    def __init__(self):
        """
        日志类初始化
        """
        pass



class LfLogger(Logger):
    def __init__(self):
        self.origin_drivers_info = None  # 存储一开始的驱动器信息方便后期计算利用率

    def print_detail_score(self, score_tuple: tuple) -> None:
        """
        打印三种任务的详细得分

        Args:
            score_tuple: 分数元组(em, fe, be, total)
        """
        print(f'em:{score_tuple[0]}')
        print(f'fe:{score_tuple[1]}')
        print(f'be:{score_tuple[2]}')
        print(f'total:{score_tuple[3]}')

    def disp_list(self, alist, info=None) -> None:
        """
        打印列表
         Args:
             alist: 需要打印的列表
             info: 说明下面打印的是什么
        Returns:
            None
        """
        if info is not None:
            print(info)
        for ele in alist:
            print(ele)

    def store_origin_drivers_info(self, drivers: dict):
        """
        保存时刻开始的驱动器信息
        Args:
            drivers: 驱动器信息
        """
        self.origin_drivers_info = copy.deepcopy(drivers)

    def print_use_rate(self, drivers: dict):
        """
        打印驱动器的空间利用率
        Args:
            drivers: 每小时结束时的驱动器信息
        Returns:
            None
        """
        ans = []
        for k in self.origin_drivers_info.keys():
            ans.append(
                (self.origin_drivers_info[k]['Capacity'] - drivers[k]['Capacity']) / self.origin_drivers_info[k]['Capacity'])
        print(f'磁盘利用率：{ans}')

    def print_rest_request_info(self, request: dict) -> None:
        """
        打印还没有处理的请求数量
        Args:
            request: 算法中的请求存储字典
        """
        print(f'剩余请求量：{len(request)}')

    def read_file_log(self, record_num: int, data_set: dict):
        """
        读取请求信息时打印日志
        """
        read_log = open('./logs/read.log', 'w', encoding='utf-8')
        read_log.write('-------------数据读取日志--------------\n')
        for t in range(record_num):
            read_log.write(f'logical clock:{t}\n')
            for ele in data_set['driver_statues_'+str(t)]:
                read_log.write(f'{str(ele)}\n')
            read_log.write('\n')
            try:  # 事实上这里不会抛出异常，因为前面加了个空列表进去
                for ele in data_set['request_list_'+str(t)]:
                    read_log.write(f'{str(ele)}\n')
            except KeyError:
                read_log.write(f'最后一对记录残缺！\n')
            read_log.write('-' * 70)
            read_log.write('\n')
        read_log.close()


