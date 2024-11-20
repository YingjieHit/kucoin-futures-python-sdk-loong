import asyncio
from ccxt.pro.binance import binance
from kucoin_futures.common.external_adapter.ccxt_binance_adapter import ccxt_binance_adapter
from kucoin_futures.strategy.event import (EventType, BinanceOrderBook5Event, BarEvent, PositionChangeEvent,
                                           CreateOrderEvent)
from kucoin_futures.strategy.object import CreateOrder
from kucoin_futures.common.app_logger import app_logger
from kucoin_futures.common.msg_client.msg_base_client import MsgBaseClient


class BinanceBaseCta(object):
    def __init__(self, symbol, key, secret, passphrase, msg_client: MsgBaseClient | None = None,
                 strategy_name="no name"):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase
        self._msg_client = msg_client
        self._strategy_name = strategy_name

        self._binance_exchange = binance()

        self._binance_trade_exchange = binance({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
        })

        self._event_queue = asyncio.Queue()
        self._order_task_queue = asyncio.Queue()
        # self._cancel_order_task_queue = asyncio.Queue()

        self._process_event_task: asyncio.Task | None = None
        self._process_execute_order_task: asyncio.Task | None = None
        self._order_book5_task: asyncio.Task | None = None
        self._bn_bar_task: asyncio.Task | None = None
        self._position_change_task: asyncio.Task | None = None
        self._schedule_task: asyncio.Task | None = None

        self._binance_markets: dict | None = None

        self._is_subscribe_binance_order_book5 = False
        self._is_subscribe_bn_kline = False
        self._is_subscribe_position = False
        self._subscribe_monitor_task: asyncio.Task | None = None  # 订阅监控协程

    async def init(self):
        # 读取市场信息
        await self._load_markets()
        # 创建定时任务
        self._schedule_task = asyncio.create_task(self._process_schedule())
        # 创建事件处理任务
        self._process_event_task = asyncio.create_task(self._process_event())
        # 创建交易执行任务
        self._process_execute_order_task = asyncio.create_task(self._execute_order())
        # 创建订阅监控任务
        self._subscribe_monitor_task = asyncio.create_task(self._subscribe_monitoring_process())

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _fetch_position(self, symbol, mgn_mode='cross'):
        positions = await self._binance_trade_exchange.fetch_positions([symbol])
        for position in positions:
            # cross 全仓, isolated 逐仓
            if position['marginMode'] == mgn_mode:
                if position is None or (position['contracts'] == 0 and position['side'] is None):
                    return 0
                elif position['side'] == 'long':
                    return position['contracts']
                elif position['side'] == 'short':
                    return -position['contracts']
                else:
                    raise ValueError(f"fetch_position error: {position}")
        return 0

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

    async def _cancel_all_orders(self, symbol: str = None):
        res = await self._binance_trade_exchange.cancel_all_orders(symbol)
        return res

    async def _process_event(self):
        while True:
            try:
                event = await self._event_queue.get()
                if event.type == EventType.BAR:
                    # 处理k线
                    await self.on_bar(event.data)
                elif event.type == EventType.BINANCE_ORDER_BOOK5:
                    # 处理order book5
                    await self.on_order_book5(event.data)

                # elif event.type == EventType.TRADE_ORDER:
                #     # 处理order回报
                #     await self.on_order(event.data)
                elif event.type == EventType.POSITION_CHANGE:
                    # 处理持仓变化
                    await self.on_position(event.data)
            except Exception as e:
                print(f"{self._strategy_name} process_event Error {str(e)}")
                self._send_msg(f"process_event Error {str(e)}")
                await app_logger.error(f"process_event Error {str(e)}")

    async def _execute_order(self):
        while True:
            try:
                event = await self._order_task_queue.get()
                if event.type == EventType.CREATE_ORDER:
                    # 发送订单
                    co: CreateOrder = event.data
                    ret = await self._binance_trade_exchange.create_order(
                        symbol=co.symbol,
                        type=co.type,
                        side=co.side,
                        amount=co.size,
                        price=co.price,
                    )
            except Exception as e:
                self._send_msg(f"{self._strategy_name} execute_order_process Error {str(e)}")
                print(f"execute_order_process Error {str(e)}")
                await app_logger.error(f"execute_order_process Error {str(e)}")

    async def _subscribe_monitoring_process(self):
        while True:
            await asyncio.sleep(60 * 60 * 24)

    async def _subscribe_bn_kline(self, symbol, kline_frequency):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        if self._bn_bar_task is not None:
            self._bn_bar_task.cancel()
            self._bn_bar_task = None

        self._bn_bar_task = asyncio.create_task(self._watch_binance_kline(symbol, kline_frequency))
        self._is_subscribe_bn_kline = True

    async def _unsubscribe_bn_kline(self):
        if self._bn_bar_task is not None:
            self._bn_bar_task.cancel()
            self._bn_bar_task = None
        self._is_subscribe_bn_kline = False

    async def _watch_binance_kline(self, symbol, kline_frequency):
        while True:
            ohlcv_list = await self._binance_exchange.watch_ohlcv(symbol, kline_frequency)
            for ohlcv in ohlcv_list:
                bar = ccxt_binance_adapter.parse_kline(ohlcv, symbol, kline_frequency)
                await self._event_queue.put(BarEvent(bar))

    async def _subscribe_binance_order_book5(self, symbol):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        if self._order_book5_task is not None:
            self._order_book5_task.cancel()
            self._order_book5_task = None
        self._order_book5_task = asyncio.create_task(self._watch_binance_order_book5(symbol))
        self._is_subscribe_binance_order_book5 = True

    async def _watch_binance_order_book5(self, symbol):
        while True:
            order_book5 = await self._binance_exchange.watch_order_book(
                symbol,
                params={
                    'limit': 5
                }
            )
            await self._event_queue.put(BinanceOrderBook5Event(order_book5))

    async def _subscribe_positions(self, symbol):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        if self._position_change_task is not None:
            self._position_change_task.cancel()
            self._position_change_task = None
        self._position_change_task = asyncio.create_task(self._watch_positions(symbol))
        self._is_subscribe_position = True

    async def _watch_positions(self, symbol):
        while True:
            positions = await self._binance_trade_exchange.watch_positions(symbols=[symbol])
            for position in positions:
                if position['symbol'] == symbol:
                    await self._event_queue.put(PositionChangeEvent(position))
                    # print(f"持仓数量: {position['contracts']}")
                    # print(f"持仓方向: {position['side']}向")
                    # print(f"时间：{position['datetime']}")
                    # print("*" * 20)

    def _send_msg(self, msg):
        if self._msg_client is not None:
            self._msg_client.send_msg(msg)

    async def _process_schedule(self):
        while True:
            await self._load_markets()
            await asyncio.sleep(60 * 60 * 24)

    async def _load_markets(self):
        self._binance_markets = await self._binance_exchange.load_markets(reload=True)

    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")

    async def on_order_book5(self, order_book5):
        raise NotImplementedError("需要实现on_order_book5")

    async def on_position(self, position_change):
        raise NotImplementedError("需要实现on_position")

    # 获取最小下单张数
    @property
    def min_contract(self):
        return self._binance_markets[self._symbol]['limits']['amount']['min']

    # 获取每张代表多少数量的币(合约乘数)
    @property
    def contract_size(self):
        return self._binance_markets[self._symbol]['contractSize']
