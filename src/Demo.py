import release.Scheduler as sd
import logger
import re
import json


global record_num  # 记录总共有几对记录

data_set = dict()

read_log = logger.LfLogger()


def get_data():
    """
    读取log文件中每条json数据并按小时存储在data_set中：\n
    data_set:{driver_statues_0:[{},{}...], request_list_0:[{},{}...], driver_statues_1:[{},{}...], ...}

    Returns:
        None
    """
    global record_num
    # 打开文件
    data_file = 'Demo数据集.log'
    with open(data_file, 'r', encoding='utf-8') as f:
        data = f.readlines()
    # 读取
    cur_driver_statues = []
    cur_request_list = []
    last = 'r'
    ind = -1
    for i in range(len(data)):
        info = extract_dict(data[i])[0]
        if last == 'r' and data[i][0] == 'd':  # 进入到一个新的clock周期
            # 新建对应的driver和request列表并设为当前周期的列表
            ind += 1
            data_set['driver_statues_'+str(ind)] = []
            data_set['request_list_'+str(ind)] = []
            cur_driver_statues = data_set['driver_statues_'+str(ind)]
            cur_request_list = data_set['request_list_'+str(ind)]
            # 加入信息
            cur_driver_statues.append(info)
            last = 'd'
        elif last == 'd' and data[i][0] == 'd':
            cur_driver_statues.append(info)
            last = 'd'
        elif last == 'd' and data[i][0] == 'r':
            cur_request_list.append(info)
            last = 'r'
        elif last == 'r' and data[i][0] == 'r':
            cur_request_list.append(extract_dict(data[i])[0])
            last = 'r'
    record_num = ind + 1  # 保存记录数目
    # read_log.read_file_log(record_num, data_set)


def extract_dict(s) -> list:
    """
    提取字符串中的字典

    Args:
        s: log文件中的一行
    Returns:
        list
    """
    results = []
    s_ = ' '.join(s.split('\n')).strip()
    exp = re.compile(r'(\{.*?\})')
    for i in exp.findall(s_):
        try:
            results.append(json.loads(i))
        except json.JSONDecodeError:
            pass
    return results


if __name__ == '__main__':
    # 读取数据
    get_data()
    # 模拟api调用
    sd_test = sd.FinalScheduler()
    # 模拟每个小时发送请求信息
    for i in range(record_num):
        if data_set['request_list_'+str(i)] is not None and data_set['driver_statues_'+str(i)] is not None:
            sd_test.schedule(i, data_set['request_list_'+str(i)], data_set['driver_statues_'+str(i)])  # 最后一对中driver是空的
