from datetime import datetime
from kucoin_futures.client import Market
from kucoin_futures.strategy.time_utils import time_utils

def main():
    market = Market()
    end_t = time_utils.get_cur_ts('ms')
    begin_t = end_t - time_utils.calc_seconds_by_freq_count('5min', 210) * 1000

    end_t = time_utils.get_ts_from_str()

    print(time_utils.get_ts_unit(begin_t))
    kline_data = market.get_kline_data('XBTUSDTM', 5, begin_t, end_t)
    print(kline_data)
    print(len(kline_data))

    ts_0 = kline_data[0][0]
    ts_1 = kline_data[1][0]
    ts_last = kline_data[-1][0]

    print(datetime.fromtimestamp(ts_0 / 1e3))
    print(datetime.fromtimestamp(ts_1 / 1e3))
    print(datetime.fromtimestamp(ts_last / 1e3))

    print(time_utils.get_ts_unit(begin_t))

if __name__ == '__main__':
    main()

