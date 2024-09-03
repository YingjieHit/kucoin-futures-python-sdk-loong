from kucoin_futures.client import Market
from kucoin_futures.strategy.time_utils import time_utils
from kucoin_futures.strategy.object import Bar


class KlineDataLoader(object):

    def __init__(self):
        self.market = Market()

    def get_last_n_bars(self, symbol: str, freq: str, ts: int, n: int) -> list[Bar]:
        # ts兼容s和ms
        # 接口ts要求是毫秒
        if time_utils.get_ts_unit(ts) == 's':
            ts = ts * 1000
        if time_utils.get_ts_unit(ts) != 'ms':
            raise ValueError("begin_ts and end_ts should be ms")
        end_ts = ts
        start_ts = end_ts - time_utils.calc_seconds_by_freq_count(freq, n) * 1000

        kline_data = []
        granularity = time_utils.get_granularity_by_freq(freq)
        while len(kline_data) < n:
            sub_kline_data = self.market.get_kline_data(symbol, granularity, start_ts, end_ts)
            if len(sub_kline_data) == 0:
                break
            kline_data.extend(sub_kline_data)
            print(sub_kline_data[-1])
            start_ts = sub_kline_data[-1][0] + 1000

        kline_data = kline_data[-n:]
        bars = []
        for kline in kline_data:
            bars.append(
                Bar(
                    symbol=symbol,
                    ts=kline[0] // 1000,
                    open=kline[1],
                    close=kline[4],
                    high=kline[2],
                    low=kline[3],
                    volume=kline[5],
                    turnover=kline[5]
                )
            )

        return bars


kline_data_loader = KlineDataLoader()

