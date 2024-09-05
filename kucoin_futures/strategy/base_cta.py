import asyncio

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.strategy.enums import Subject
from kucoin_futures.strategy.market_data_parser import market_data_parser
from kucoin_futures.strategy.event import (EventType, TickerEvent, TraderOrderEvent, CreateMarketMakerOrderEvent,
                                           Level2Depth5Event, BarEvent, CreateOrderEvent, CancelOrderEvent, CancelAllOrderEvent)
from kucoin_futures.strategy.object import Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder
from kucoin_futures.trade.async_trade import TradeDataAsync
from kucoin_futures.common.app_logger import app_logger


class BaseCta(object):
    def __init__(self, symbol, key, secret, passphrase):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase

        self._trade = TradeDataAsync(key=key, secret=secret, passphrase=passphrase)
        self._event_queue = asyncio.Queue()
        self._order_task_queue = asyncio.Queue()
        self._cancel_order_task_queue = asyncio.Queue()

        self._client = WsToken(key=key,
                               secret=secret,
                               passphrase=passphrase,
                               url='https://api-futures.kucoin.com')
        self._ws_public_client: KucoinFuturesWsClient | None = None
        self._ws_private_client: KucoinFuturesWsClient | None = None
        self._process_event_task: asyncio.Task | None = None
        self._process_execute_order_task: asyncio.Task | None = None
        self._process_cancel_order_task: asyncio.Task | None = None

    async def _create_ws_client(self):
        # 创建ws_client
        self._ws_public_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_public_msg,
                                                                    private=False)
        self._ws_private_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_private_msg,
                                                                     private=True)

    async def init(self):
        # 创建事件处理任务
        self._process_event_task = asyncio.create_task(self._process_event())
        # 创建交易执行任务
        self._process_execute_order_task = asyncio.create_task(self._execute_order())
        # 创建撤单执行任务
        self._process_cancel_order_task = asyncio.create_task(self._process_cancel_order())
        # 创建ws_client
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
        # data = msg.get('data')
        # print("_deal_private_msg")
        # print(msg)
        try:
            if msg.get('subject') == Subject.symbolOrderChange:
                order = market_data_parser.parse_order(msg)
                await self._event_queue.put(TraderOrderEvent(order))
            elif msg.get('subject') == Subject.positionChange:
                print(f"positionChange: {msg}")
            else:
                print(f"_deal_private_msg 未知的subject: {msg.get('subject')}")
        except Exception as e:
            await app_logger.error(f"_deal_private_msg Error {str(e)}")

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

    async def _execute_order(self):
        while True:
            try:
                event = await self._order_task_queue.get()
                if event.type == EventType.CREATE_MARKET_MAKER_ORDER:
                    # 发送做市单
                    mmo: MarketMakerCreateOrder = event.data
                    res = await self._trade.create_market_maker_order(mmo.symbol, mmo.lever, mmo.size, mmo.price_buy,
                                                                     mmo.price_sell, mmo.client_oid_buy,
                                                                     mmo.client_oid_sell, mmo.post_only)
                    # await app_logger.info_logger(f"订单执行结果{res}")
                elif event.type == EventType.CREATE_ORDER:
                    # 发送订单
                    co: CreateOrder = event.data
                    if co.type == 'limit':
                        await self._trade.create_limit_order(co.symbol, co.side, co.lever, co.size, co.price,
                                                            co.client_oid,
                                                            postOnly=co.post_only)
                    elif co.type == 'market':
                        await  self._trade.create_market_order(co.symbol, co.side, co.lever, co.client_oid,
                                                                  postOnly=co.post_only)
            except Exception as e:
                await app_logger.error(f"execute_order_process Error {str(e)}")

    async def _process_cancel_order(self):
        while True:
            try:
                event = await self._cancel_order_task_queue.get()

                if event.type == EventType.CANCEL_ALL_ORDER:
                    # 撤销所有订单
                    symbol = event.data
                    await self._trade.cancel_all_limit_order(symbol)

                elif event.type == EventType.CANCEL_ORDER:
                    # 撤单
                    co: CancelOrder = event.data
                    if co.client_oid:
                        res = await self._trade.cancel_order_by_clientOid(co.client_oid, co.symbol)
                    else:
                        await self._trade.cancel_order(co.order_id)
            except Exception as e:
                await app_logger.error(f"process_cancel_order Error {str(e)}")

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

    async def _subscribe_position(self, symbol):
        await self._ws_private_client.subscribe(f'/contract/position:{symbol}')

    async def _unsubscribe_position(self, symbol):
        await self._ws_private_client.unsubscribe(f'/contract/position:{symbol}')

    async def _create_order(self, symbol, side, size, type, price, lever, client_oid='', post_only=True):
        co = CreateOrder(
            symbol=symbol,
            lever=lever,
            size=size,
            side=side,
            price=price,
            type=type,
            client_oid=client_oid,
            post_only=post_only
        )
        await self._order_task_queue.put(CreateOrderEvent(co))

    async def _cancel_all_order(self, symbol: str = None):
        if not symbol:
            symbol = self._symbol
        await self._cancel_order_task_queue.put(CancelAllOrderEvent(symbol))

    async def _cancel_order_by_order_id(self, order_id: str):
        # await self.cancel_order_task_queue.put(CancelOrder(order_id=order_id))
        data = CancelOrder(order_id=order_id)
        await self._cancel_order_task_queue.put(CancelOrderEvent(data))

    async def _cancel_order_by_client_oid(self, symbol, client_oid):
        # await self.cancel_order_task_queue.put(CancelOrder(symbol=symbol, client_oid=client_oid))
        data = CancelOrder(symbol=symbol, client_oid=client_oid)
        await self._cancel_order_task_queue.put(CancelOrderEvent(data))

    async def _get_position_qty(self):
        pos = await self._trade.get_position_details(self._symbol)
        data = pos.get('data')
        qty = data.get('currentQty')
        return qty
