from ccxt.pro import binance
from kucoin_futures.strategy.time_utils import time_utils
from kucoin_futures.strategy.object import Bar


class AsyncKlineDataLoader(object):
    def __init__(self, binance_exchange: binance = None):
        self.binance = binance() if binance_exchange is None else binance_exchange

    async def get_bn_last_n_bars_from_ccxt(self, symbol: str, freq: str, ts: int, n: int) -> list[Bar]:
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
            sub_kline_data = await self.binance.fetch_ohlcv(
                symbol=symbol,
                timeframe=freq,
                since=start_ts,
                limit=1500,  # TODO: 这里可以优化
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
