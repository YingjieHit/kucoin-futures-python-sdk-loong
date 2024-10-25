import asyncio
from ccxt.pro.okx import okx
from ccxt.pro.binance import binance
from kucoin_futures.strategy.event import (EventType, TickerEvent, TraderOrderEvent, CreateMarketMakerOrderEvent,
                                           Level2Depth5Event, BarEvent, PositionChangeEvent,
                                           CreateOrderEvent, CancelOrderEvent, CancelAllOrderEvent)
from kucoin_futures.strategy.object import Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder
from kucoin_futures.common.app_logger import app_logger


class OkxBaseCta(object):
    def __init__(self, symbol, key, secret, passphrase):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase

        self._oxk_exchange = okx({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
        })
        self._binance_exchange = binance()

        self._event_queue = asyncio.Queue()
        self._order_task_queue = asyncio.Queue()
        self._cancel_order_task_queue = asyncio.Queue()

        self._process_event_task: asyncio.Task | None = None

    async def init(self):
        # 创建事件处理任务
        self._process_event_task = asyncio.create_task(self._process_event())

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _process_event(self):
        pass

    async def _subscribe_bn_kline(self, symbol, kline_frequency):
        await asyncio.create_task(self._watch_binance_kline(symbol, kline_frequency))

    async def _watch_binance_kline(self, symbol, kline_frequency):
        while True:
            ohlcv = await self._binance_exchange.watch_ohlcv(symbol, kline_frequency)
            print(ohlcv)
            print(type(ohlcv))