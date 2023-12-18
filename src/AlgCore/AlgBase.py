from abc import ABCMeta, abstractmethod


class AlgBase:
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_score(self) -> int:
        """
        :return 当前的总得分
        """
        pass

    @abstractmethod
    def task_assign(self, logical_clock: int, request_list: list, driver_statues: list):
        """
        对请求信息进行预处理以及通过某种数据结构存储
        优化方向：
        请求信息的存储方式：堆/树/懒惰删除/高级数据结构？
        可以尝试对各种请求进行处理的优先级别：紧迫程度、加分/扣分收益权衡、需要的驱动器空间-----综合考虑？
        :param logical_clock 时刻
        :param request_list 请求列表
        :param driver_statues 驱动器信息
        """
        pass

    @abstractmethod
    def op_task(self, logical_clock: int, request_list: list, driver_statues: list) -> list:
        """
        驱动器调度算法\n
        优化方向：\n
        如何选择请求去填充驱动器使当前时刻的驱动器有最大利用率：二分搜索优化/启发式算法？
        :return 返回该小时的调度json信息
        """