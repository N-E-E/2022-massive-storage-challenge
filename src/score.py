"""
计分器：
- 在处理任务时根据时间计分
"""

import math


class Score:
    def __init__(self):
        self.fe_punish_score = 0
        self.em_punish_score = 0
        self.praise_score = 0

    def get_detail_score(self) -> tuple[int, int, int, int]:
        """
        返回详细分数：em, fe, be, total
        """
        return -self.em_punish_score, -self.fe_punish_score, self.praise_score, \
               -self.fe_punish_score - self.em_punish_score + self.praise_score

    def mark(self, task_info: dict, cur_time: int):
        """
        计算task_info这条信息在cur_time时刻完成/丢弃时的扣分/加分
        Args:
            task_info: 任务信息
            cur_time: 当前时刻
        """
        delta = max(cur_time - task_info['LogicalClock'] - task_info['SLA'] + 1, 0)  # delta为超时的时间
        if task_info['RequestType'] == 'EM':
            if delta >= 12:
                self.em_punish_score += 2 * 12 * math.ceil(task_info['RequestSize'] / 50)
            elif delta >= 1:
                self.em_punish_score += 2 * delta * math.ceil(task_info['RequestSize'] / 50)
        elif task_info['RequestType'] == 'FE':
            if delta >= 12:
                self.fe_punish_score += 12 * math.ceil(task_info['RequestSize'] / 50)
            elif delta >= 1:
                self.fe_punish_score += delta * math.ceil(task_info['RequestSize'] / 50)
        elif task_info['RequestType'] == 'BE':
            if cur_time - task_info['LogicalClock'] < 12:
                self.praise_score += 0.5 * math.ceil(task_info['RequestSize'] / 50)
        else:
            print("error")
