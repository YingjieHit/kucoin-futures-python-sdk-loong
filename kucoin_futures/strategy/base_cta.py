import asyncio

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.strategy.enums import Subject
from kucoin_futures.strategy.market_data_parser import market_data_parser
from kucoin_futures.strategy.event import (EventType, TickerEvent, TraderOrderEvent, CreateMarketMakerOrderEvent,
                                           Level2Depth5Event, BarEvent)
from kucoin_futures.common.app_logger import app_logger


class BaseCta(object):
    def __init__(self, symbol, key, secret, passphrase, kline_frequency, kline_size):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase
        self._kline_frequency = kline_frequency  # K线周期,1min 5min 15min 30min 1h 2h 4h 1d
        self._kline_size = kline_size

        self._event_queue = asyncio.Queue()

        self._client = WsToken(key=key,
                               secret=secret,
                               passphrase=passphrase,
                               url='https://api-futures.kucoin.com')
        self._ws_public_client: KucoinFuturesWsClient | None = None
        self._ws_private_client: KucoinFuturesWsClient | None = None
        self._process_event_task: asyncio.Task | None = None

    async def _create_ws_client(self):
        # 创建ws_client
        self._ws_public_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_public_msg,
                                                                    private=False)
        self._ws_private_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_private_msg,
                                                                     private=True)

    async def init(self):
        self._process_event_task = asyncio.create_task(self._process_event())
        await self._create_ws_client()

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _deal_public_msg(self, msg):
        # data = msg.get('data')
        # print(msg)
        try:
            if msg.get('subject') == Subject.level2:
                level2_depth5 = market_data_parser.parse_level2_depth5(msg)
                await self._event_queue.put(Level2Depth5Event(level2_depth5))
            elif msg.get('subject') == Subject.candleStick:
                bar = market_data_parser.parse_bar(msg)
                await self._event_queue.put(BarEvent(bar))
            else:
                raise Exception(f"未知的subject {msg.get('subject')}")
        except Exception as e:
            await app_logger.error(f"deal_public_msg Error {str(e)}")

    async def _deal_private_msg(self, msg):
        data = msg.get('data')
        print("_deal_private_msg")
        print(msg)
        try:
            if msg.get('subject') == Subject.symbolOrderChange:
                order = market_data_parser.parse_order(msg)
                await self._event_queue.put(TraderOrderEvent(order))
        except Exception as e:
            await app_logger.error(f"deal_private_msg Error {str(e)}")

    async def _process_event(self):
        while True:
            try:
                event = await self._event_queue.get()
                if event.type == EventType.LEVEL2DEPTH5:
                    # 处理ticker
                    await self.on_level2_depth5(event.data)
                elif event.type == EventType.BAR:
                    # 处理k线
                    await self.on_bar(event.data)
                elif event.type == EventType.TRADE_ORDER:
                    # 处理order回报
                    await self.on_order(event.data)
            except Exception as e:
                await app_logger.error(f"process_event Error {str(e)}")

    async def on_level2_depth5(self, level2_depth5):
        raise NotImplementedError("需要实现on_level2_depth5")

    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")

    async def on_order(self, order):
        raise NotImplementedError("需要实现on_order")

    async def _subscribe_kline(self, symbol, kline_frequency):
        # topic举例 '/contractMarket/limitCandle:XBTUSDTM_1hour'
        await self._ws_public_client.subscribe(f'/contractMarket/limitCandle:{symbol}_{kline_frequency}')

    async def _unsubscribe_kline(self, symbol, kline_frequency):
        await self._ws_public_client.unsubscribe(f'/contractMarket/limitCandle:{symbol}_{kline_frequency}')

    async def _subscribe_level2_depth5(self, symbol):
        # topic举例 '/contractMarket/level2Depth5:XBTUSDTM'
        await self._ws_public_client.subscribe(f'/contractMarket/level2Depth5:{symbol}')

    async def _unsubscribe_level2_depth5(self, symbol):
        await self._ws_public_client.unsubscribe(f'/contractMarket/level2Depth5:{symbol}')

    async def _subscribe_trade_orders(self, symbol):
        # topic举例 '/contractMarket/tradeOrders:XBTUSDTM'
        await self._ws_private_client.subscribe(f'/contractMarket/tradeOrders:{symbol}')

    async def _unsubscribe_trade_orders(self, symbol):
        await self._ws_private_client.unsubscribe(f'/contractMarket/tradeOrders:{symbol}')
