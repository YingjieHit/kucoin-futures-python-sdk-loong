from datetime import datetime
from kucoin_futures.client import Market
from kucoin_futures.strategy.time_utils import time_utils
from kucoin_futures.strategy.kline_data_loader import kline_data_loader

def main():
    market = Market()
    # end_t = time_utils.get_cur_ts('ms')
    # begin_t = end_t - time_utils.calc_seconds_by_freq_count('5min', 210) * 1000
    # TODO: 因为一次只能申请200根K线，所以需要实现多次请求，考虑用申请到的最早的K的时间作为下一次的请求时间
    end_t = time_utils.get_ts_from_str('2024-08-25 00:00:10', 'ms')
    # begin_t = time_utils.get_ts_from_str('2021-08-25 00:00:10', 'ms')
    begin_t = end_t - time_utils.calc_seconds_by_freq_count('5min', 1000) * 1000

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


def main2():
    ts = time_utils.get_cur_ts('ms')
    bars = kline_data_loader.get_last_n_bars('XBTUSDTM', '5min', ts, 10)

    print(bars)

if __name__ == '__main__':
    main()

