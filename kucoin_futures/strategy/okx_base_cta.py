import asyncio
from ccxt.pro.okx import okx
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

        self._process_event_task: asyncio.Task | None = None

    async def init(self):
        # 创建事件处理任务
        self._process_event_task = asyncio.create_task(self._process_event())

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _process_event(self):
        pass
