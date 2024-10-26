import asyncio
from ccxt.pro.okx import okx
from ccxt.pro.binance import binance
from kucoin_futures.common.external_adapter.ccxt_binance_adapter import ccxt_binance_adapter
from kucoin_futures.strategy.event import (EventType, TickerEvent, TraderOrderEvent, CreateMarketMakerOrderEvent,
                                           OkxOrderBook5Event, BarEvent, PositionChangeEvent,
                                           CreateOrderEvent, CancelOrderEvent, CancelAllOrderEvent)
from kucoin_futures.strategy.object import Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder, Bar
from kucoin_futures.common.app_logger import app_logger


class OkxBaseCta(object):
    def __init__(self, symbol, key, secret, passphrase):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase

        self._okx_exchange = okx({
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
        self._process_execute_order_task: asyncio.Task | None = None
        self._order_book5_task: asyncio.Task | None = None
        self._bn_bar_task: asyncio.Task | None = None
        self._position_change_task: asyncio.Task | None = None
        self._schedule_task: asyncio.Task | None = None

        self._okx_markets: dict | None = None

    async def init(self):
        # 读取市场信息
        await self._load_markets()
        # 创建定时任务
        self._schedule_task = asyncio.create_task(self._process_schedule())
        # 创建事件处理任务
        self._process_event_task = asyncio.create_task(self._process_event())
        # 创建交易执行任务
        self._process_execute_order_task = asyncio.create_task(self._execute_order())

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _create_order(self, symbol, side, size, type, price=None, lever=1, client_oid='', post_only=False):
        if type != 'market' and price is None:
            raise ValueError("price can not be None when type is not 'market'")
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

    async def _process_event(self):
        while True:
            try:
                event = await self._event_queue.get()
                if event.type == EventType.BAR:
                    # 处理k线
                    await self.on_bar(event.data)
                elif event.type == EventType.OKX_ORDER_BOOK5:
                    # 处理order book5
                    await self.on_order_book5(event.data)

                # elif event.type == EventType.TRADE_ORDER:
                #     # 处理order回报
                #     await self.on_order(event.data)
                elif event.type == EventType.POSITION_CHANGE:
                    # 处理持仓变化
                    await self.on_position_change(event.data)
            except Exception as e:
                print(f"process_event Error {str(e)}")
                await app_logger.error(f"process_event Error {str(e)}")

    async def _execute_order(self):
        while True:
            try:
                event = await self._order_task_queue.get()
                if event.type == EventType.CREATE_ORDER:
                    # 发送订单
                    co: CreateOrder = event.data
                    await self._okx_exchange.create_order(
                        symbol=co.symbol,
                        type=co.type,
                        side=co.side,
                        amount=co.size,
                        price=co.price,
                    )
            except Exception as e:
                print(f"execute_order_process Error {str(e)}")
                await app_logger.error(f"execute_order_process Error {str(e)}")

    async def _subscribe_bn_kline(self, symbol, kline_frequency):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        self._bn_bar_task = asyncio.create_task(self._watch_binance_kline(symbol, kline_frequency))

    async def _watch_binance_kline(self, symbol, kline_frequency):
        while True:
            ohlcv_list = await self._binance_exchange.watch_ohlcv(symbol, kline_frequency)
            for ohlcv in ohlcv_list:
                bar = ccxt_binance_adapter.parse_kline(ohlcv, symbol, kline_frequency)
                await self._event_queue.put(BarEvent(bar))

    async def _subscribe_okx_order_book5(self, symbol):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        # print("subscribe okx_order_book5")
        self._order_book5_task = asyncio.create_task(self._watch_okx_order_book5(symbol))

    async def _watch_okx_order_book5(self, symbol):
        while True:
            order_book5 = await self._okx_exchange.watch_order_book(
                symbol,
                params={'channel': 'books5'},
            )
            await self._event_queue.put(OkxOrderBook5Event(order_book5))

    async def _subscribe_positions(self, symbol):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        self._position_change_task = asyncio.create_task(self._watch_positions(symbol))

    async def _watch_positions(self, symbol):
        while True:
            positions = await self._okx_exchange.watch_positions(symbols=[symbol])
            for position in positions:
                if position['symbol'] == symbol:
                    await self._event_queue.put(PositionChangeEvent(position))
                    # print(f"持仓数量: {position['contracts']}")
                    # print(f"持仓方向: {position['side']}向")
                    # print(f"时间：{position['datetime']}")
                    # print("*" * 20)

    async def _process_schedule(self):
        while True:
            await self._load_markets()
            await asyncio.sleep(60 * 60 * 24)

    async def _load_markets(self):
        self._okx_markets = await self._okx_exchange.load_markets(reload=True)

    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")

    async def on_order_book5(self, order_book5):
        raise NotImplementedError("需要实现on_order_book5")

    async def on_position_change(self, position_change):
        raise NotImplementedError("需要实现on_position_change")

    # 获取最小下单张数
    @property
    def min_contract(self):
        return self._okx_markets[self._symbol]['limits']['amount']['min']

    # 获取每张代表多少数量的币(合约乘数)
    @property
    def contract_size(self):
        return self._okx_markets[self._symbol]['contractSize']
