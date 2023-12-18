import copy
import functools
import time
import math
from abc import ABCMeta, abstractmethod
from AlgCore.loss_func_method_3 import LossFuncMethod3


class Scheduler(metaclass=ABCMeta):
    @abstractmethod
    def init(self, driver_num: int) -> None:
        pass

    @abstractmethod
    def schedule(self, logical_clock: int, request_list: list, driver_statues: list) -> list:
        pass


class FinalScheduler(Scheduler):
    def __init__(self):
        self.driver_num = 0
        self.ans = []
        self.method = LossFuncMethod3()  # 需要优化的点，想测试自己的算法改这个就行

    def init(self, driver_num: int):
        self.driver_num = driver_num
        time.sleep(1)

    def schedule(self, logical_clock: int, request_list: list, driver_statues: list) -> list:
        time.sleep(1)
        # 任务分类
        self.method.task_assign(logical_clock, request_list, driver_statues)
        # 处理任务
        self.ans = self.method.op_task(logical_clock, request_list, driver_statues)
        score = self.method.get_score()
        print('-'*70)
        return self.ans

