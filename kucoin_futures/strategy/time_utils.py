import os
from datetime import datetime, timedelta


class TimeUtils(object):

    # 获取当前时间戳 int
    @staticmethod
    def get_cur_timestamp():
        return int(datetime.now().timestamp())

    # 传入频率和数量，返回秒数
    @staticmethod
    def calc_seconds_by_freq_count(freq: str, n: int):
        # 1min, 3min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
        if freq not in ['1min', '3min', '5min', '15min', '30min', '1hour', '2hour', '4hour', '6hour', '8hour', '12hour',
                        '1day', '1week']:
            raise ValueError(
                "freq not in ['1min', '3min', '5min', '15min', '30min', '1hour', '2hour', '4hour', '6hour', '8hour', '12hour', '1day', '1week']")

        return {
            '1min': 60,
            '3min': 3 * 60,
            '5min': 5 * 60,
            '15min': 15 * 60,
            '30min': 30 * 60,
            '1hour': 60 * 60,
            '2hour': 2 * 60 * 60,
            '4hour': 4 * 60 * 60,
            '6hour': 6 * 60 * 60,
            '8hour': 8 * 60 * 60,
            '12hour': 12 * 60 * 60,
            '1day': 24 * 60 * 60,
            '1week': 7 * 24 * 60 * 60,
        }[freq] * n

    # 获取日期字符串
    # TODO: 兼容所有级别时间戳
    @staticmethod
    def get_date_str_from_ts_ms(ts):
        ts_seconds = int(ts / 1e3)  # 假设ts是毫秒级别的时间戳，转换为秒级时间戳
        date_str = datetime.utcfromtimestamp(ts_seconds).strftime('%Y-%m-%d')
        return date_str

    # 传入int时间戳，判断时间戳的单位是s ms ns
    @staticmethod
    def get_ts_unit(ts: int):
        # 获取时间戳的位数
        length = len(str(ts))

        if length == 10:
            return 's'  # 秒级时间戳
        elif length == 13:
            return 'ms'  # 毫秒级时间戳
        elif length == 19:
            return 'ns'  # 纳秒级时间戳
        else:
            return 'Unknown'  # 无法识别的时间戳格式


time_utils = TimeUtils()
