from kucoin_futures.client import Market
from kucoin_futures.strategy.time_utils import time_utils

def main():
    market = Market()
    begin_t = time_utils.get_cur_timestamp()
    end_t = time_utils.get_cur_timestamp() - time_utils.calc_seconds_by_freq_count('1day', 1)
    kline_data = market.get_kline_data('XBTUSDTM', 5, )
    print(kline_data)
    print(len(kline_data))



if __name__ == '__main__':
    main()

