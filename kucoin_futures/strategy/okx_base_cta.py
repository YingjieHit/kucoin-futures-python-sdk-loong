import asyncio
from ccxt.pro.okx import okx
from ccxt.pro.binance import binance
from kucoin_futures.common.external_adapter.ccxt_binance_adapter import ccxt_binance_adapter
from kucoin_futures.strategy.event import (EventType, TickerEvent, TraderOrderEvent, CreateMarketMakerOrderEvent,
                                           Level2Depth5Event, BarEvent, PositionChangeEvent,
                                           CreateOrderEvent, CancelOrderEvent, CancelAllOrderEvent)
from kucoin_futures.strategy.object import Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder, Bar
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
        while True:
            try:
                event = await self._event_queue.get()
                if event.type == EventType.BAR:
                    # 处理k线
                    await self.on_bar(event.data)
                elif event.type == EventType.LEVEL2DEPTH5:
                    # 处理ticker
                    # await self.on_level2_depth5(event.data)
                    pass
                # elif event.type == EventType.TRADE_ORDER:
                #     # 处理order回报
                #     await self.on_order(event.data)
                # elif event.type == EventType.POSITION_CHANGE:
                #     # 处理持仓变化
                #     await self.on_position_change(event.data)
            except Exception as e:
                await app_logger.error(f"process_event Error {str(e)}")

    async def _subscribe_bn_kline(self, symbol, kline_frequency):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        await asyncio.create_task(self._watch_binance_kline(symbol, kline_frequency))

    async def _watch_binance_kline(self, symbol, kline_frequency):
        while True:
            ohlcv_list = await self._binance_exchange.watch_ohlcv(symbol, kline_frequency)
            for ohlcv in ohlcv_list:
                bar = ccxt_binance_adapter.parse_kline(ohlcv, symbol, kline_frequency)
                await self._event_queue.put(BarEvent(bar))


    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")