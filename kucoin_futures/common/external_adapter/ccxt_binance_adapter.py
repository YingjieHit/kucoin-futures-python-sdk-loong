from kucoin_futures.strategy.object import Bar


class CcxtBinanceAdapter(object):

    def __init__(self):
        pass

    # ccxt binance的k线数据转化为该项目的Bar
    @staticmethod
    def parse_kline(ccxt_kline: list, symbol: str|None=None, frequency: str|None=None) -> Bar:
        return Bar(
            symbol=symbol,
            ts=ccxt_kline[0]//1000,
            open=ccxt_kline[1],
            high=ccxt_kline[2],
            low=ccxt_kline[3],
            close=ccxt_kline[4],
            volume=ccxt_kline[5],
            frequency=frequency,
        )


ccxt_binance_adapter = CcxtBinanceAdapter()
