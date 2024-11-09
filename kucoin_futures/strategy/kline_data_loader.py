from kucoin_futures.client import Market
from kucoin_futures.strategy.time_utils import time_utils
from kucoin_futures.strategy.object import Bar
from kucoin_futures.common.const import KC_TO_BN_SYMBOL, KC_TO_BN_FREQUENCY
from binance.cm_futures import CMFutures
from ccxt import binance


class KlineDataLoader(object):

    def __init__(self, binance_exchange: binance=None):
        self.market = Market()
        self.bn_cm_futures = CMFutures()
        self.binance = binance() if binance_exchange is None else binance_exchange

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

    def get_bn_cm_last_n_bars(self, symbol: str, freq: str, ts: int, n: int) -> list[Bar]:
        # 接口ts要求是毫秒
        if time_utils.get_ts_unit(ts) == 's':
            ts = ts * 1000
        if time_utils.get_ts_unit(ts) != 'ms':
            raise ValueError("begin_ts and end_ts should be ms")
        # end_ts = ts
        start_ts = ts - time_utils.calc_seconds_by_freq_count(freq, n) * 1000
        max_ts = time_utils.calc_seconds_by_freq_count(freq, 1499) * 1000
        end_ts = ts if start_ts + max_ts >= ts else start_ts + max_ts

        symbol = KC_TO_BN_SYMBOL[symbol]
        freq = KC_TO_BN_FREQUENCY[freq]
        kline_data = []
        while len(kline_data) < n:
            sub_kline_data = self.bn_cm_futures.klines(
                symbol=symbol,
                interval=freq,
                startTime=start_ts,
                endTime=end_ts,
                limit= 1500,  # TODO: 这里可以优化
            )
            if len(sub_kline_data) == 0:
                break
            kline_data.extend(sub_kline_data)
            start_ts = sub_kline_data[-1][0] + 1000
            end_ts = ts if start_ts + max_ts >= ts else start_ts + max_ts

        kline_data = kline_data[-n:]
        bars = []
        for kline in kline_data:
            bars.append(
                Bar(
                    symbol=symbol,
                    ts=kline[0] // 1000,
                    open=float(kline[1]),
                    close=float(kline[4]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    volume=int(kline[5]),
                    turnover=float(kline[7])
                )
            )

        return bars

    def get_bn_last_n_bars_from_ccxt(self, symbol: str, freq: str, ts: int, n: int) -> list[Bar]:
        # 获取交易所对象
        # 接口ts要求是毫秒
        if time_utils.get_ts_unit(ts) == 's':
            ts = ts * 1000
        if time_utils.get_ts_unit(ts) != 'ms':
            raise ValueError("begin_ts and end_ts should be ms")
        # end_ts = ts
        start_ts = ts - time_utils.calc_seconds_by_freq_count(freq, n) * 1000
        max_ts = time_utils.calc_seconds_by_freq_count(freq, 1499) * 1000
        end_ts = ts if start_ts + max_ts >= ts else start_ts + max_ts

        kline_data = []
        while len(kline_data) < n:
            sub_kline_data = self.binance.fetch_ohlcv(
                symbol=symbol,
                timeframe=freq,
                since=start_ts,
                limit= 1500,  # TODO: 这里可以优化
                params={
                    'endTime': end_ts
                }
            )
            if len(sub_kline_data) == 0:
                break
            kline_data.extend(sub_kline_data)
            start_ts = sub_kline_data[-1][0] + 1000
            end_ts = ts if start_ts + max_ts >= ts else start_ts + max_ts

        kline_data = kline_data[-n:]
        bars = []
        for kline in kline_data:
            bars.append(
                Bar(
                    symbol=symbol,
                    ts=kline[0] // 1000,
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=int(kline[5]),
                    frequency=freq,
                )
            )

        return bars


kline_data_loader = KlineDataLoader()
