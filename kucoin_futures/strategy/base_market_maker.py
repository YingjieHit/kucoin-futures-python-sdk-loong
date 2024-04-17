import asyncio

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.trade.async_trade import TradeDataAsync

from kucoin_futures.strategy.event import (EventType, TickerEvent, TraderOrderEvent, CreateMarketMakerOrderEvent,
                                           CreateOrderEvent,
                                           CancelAllOrderEvent, CancelOrderEvent)
from kucoin_futures.strategy.enums import Subject
from kucoin_futures.strategy.utils import utils
from kucoin_futures.strategy.object import Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder


class BaseMarketMaker(object):
    def __init__(self, symbol, key, secret, passphrase):
        self.symbol = symbol
        self.event_queue = asyncio.Queue()  # 用于存储数据计算因子
        self.order_task_queue = asyncio.Queue()  # 用于下单任务通讯
        self.client = WsToken(key=key,
                              secret=secret,
                              passphrase=passphrase,
                              url='https://api-futures.kucoin.com')
        self.trade = TradeDataAsync(key=key, secret=secret, passphrase=passphrase)
        self.ws_public_client = None
        self.ws_private_client = None
        self.enable = False

    async def run(self):
        # 创建事件处理任务
        process_event_task = asyncio.create_task(self.process_event())
        # 创建交易执行任务
        execute_order_task = asyncio.create_task(self.execute_order())

        # 创建ws_client
        self.ws_public_client = await KucoinFuturesWsClient.create(None, self.client, self.deal_public_msg,
                                                                   private=False)
        self.ws_private_client = await KucoinFuturesWsClient.create(None, self.client, self.deal_private_msg,
                                                                    private=True)

        # 订阅orderbook
        await self.ws_public_client.subscribe(f'/contractMarket/tickerV2:{self.symbol}')

        # 订阅private tradeOrders
        await self.ws_private_client.subscribe(f'/contractMarket/tradeOrders:{self.symbol}')

        self.enable = True

        while True:
            await asyncio.sleep(60 * 60 * 24)

    async def execute_order(self):
        while True:
            event = await self.order_task_queue.get()
            if event.type == EventType.CREATE_MARKET_MAKER_ORDER:
                # 发送做市单
                mmo: MarketMakerCreateOrder = event.data
                await self.trade.create_market_maker_order(mmo.symbol, mmo.lever, mmo.size, mmo.price_buy,
                                                           mmo.price_sell, mmo.client_oid_buy,
                                                           mmo.client_oid_sell, mmo.post_only)
            elif event.type == EventType.CREATE_ORDER:
                # 发送订单
                co: CreateOrder = event.data
                if co.type == 'limit':
                    await self.trade.create_limit_order(co.symbol, co.side, co.lever, co.size, co.price, co.client_oid,
                                                        postOnly=co.post_only)
                elif co.type == 'market':
                    await  self.trade.create_market_order(co.symbol, co.side, co.lever, co.client_oid,
                                                          postOnly=co.post_only)

            elif event.type == EventType.CANCEL_ALL_ORDER:
                # 撤销所有订单
                symbol = event.data
                await self.trade.cancel_all_limit_order(symbol)

            elif event.type == EventType.CANCEL_ORDER:
                # 撤单
                co: CancelOrder = event.data
                if co.client_oid:
                    await self.trade.cancel_order_by_clientOid(co.client_oid, co.symbol)
                else:
                    await self.trade.cancel_order(co.order_id)

    async def on_tick(self, ticker: Ticker):
        print("需要实现on_tick")

    async def on_order(self, order: Order):
        print("需要实现on_order")

    async def process_event(self):
        """处理事件"""
        while True:
            event = await self.event_queue.get()
            if event.type == EventType.TICKER:
                # 处理ticker
                await self.on_tick(event.data)
            elif event.type == EventType.TRADE_ORDER:
                # 处理order回报
                await self.on_order(event.data)

    async def deal_public_msg(self, msg):
        data = msg.get('data')
        if msg.get('subject') == Subject.tickerV2:
            ticker = utils.dict_2_ticker(data)
            await self.event_queue.put(TickerEvent(ticker))

    async def deal_private_msg(self, msg):
        data = msg.get('data')
        if msg.get('subject') == Subject.symbolOrderChange:
            order = utils.dict_2_order(data)
            await self.event_queue.put(TraderOrderEvent(order))

    async def create_market_maker_order(self, symbol, lever, size, price_buy, price_sell,
                                        client_oid_buy='', client_oid_sell='', post_only=True):
        mm_order = MarketMakerCreateOrder(
            symbol=symbol,
            lever=lever,
            size=size,
            price_buy=price_buy,
            price_sell=price_sell,
            client_oid_buy=client_oid_buy,
            client_oid_sell=client_oid_sell,
            post_only=post_only
        )
        await self.order_task_queue.put(CreateMarketMakerOrderEvent(mm_order))

    async def cancel_all_order(self, symbol: str = None):
        if not symbol:
            symbol = self.symbol
        await self.order_task_queue.put(CancelAllOrderEvent(symbol))

    async def cancel_order_by_order_id(self, order_id: str):
        await self.order_task_queue.put(CancelOrder(order_id=order_id))

    async def cancel_order_by_client_oid(self, symbol, client_oid):
        await self.order_task_queue.put(CancelOrder(symbol=symbol, client_oid=client_oid))
