import asyncio
from ccxt.pro import kucoinfutures
from ccxt.pro.binance import binance
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.strategy.enums import Subject
from kucoin_futures.strategy.market_data_parser import market_data_parser
from kucoin_futures.strategy.event import (Level2Depth5Event, BarEvent, PositionChangeEvent,
                                           CreateOrderEvent, CancelOrderEvent, CancelAllOrderEvent)
from kucoin_futures.strategy.object import Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder, Level2Depth5
from kucoin_futures.common.external_adapter.ccxt_binance_adapter import ccxt_binance_adapter
from kucoin_futures.strategy.event import (EventType,BarEvent, PositionChangeEvent,
                                           CreateOrderEvent, CancelOrderEvent, CancelAllOrderEvent)
from kucoin_futures.common.app_logger import app_logger
from kucoin_futures.common.msg_base_client import MsgBaseClient


class KucoinfuturesBaseCta(object):
    def __init__(self, symbol, key, secret, passphrase, msg_client: MsgBaseClient | None = None,
                 strategy_name="no name"):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase
        self._msg_client = msg_client
        self._strategy_name = strategy_name

        self._kucoinfutures_exchange = kucoinfutures({
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

        self._kucoinfutures_level2_depth5_task: asyncio.Task | None = None
        self._bn_bar_task: asyncio.Task | None = None
        self._position_change_task: asyncio.Task | None = None
        self._schedule_task: asyncio.Task | None = None

        self._kucoinfutures_markets: dict | None = None

        self._is_subscribe_kucoinfutures_level2_depth5 = False
        self._is_subscribe_bn_kline = False
        self._is_subscribe_position = False
        self._subscribe_monitor_task: asyncio.Task | None = None  # 订阅监控协程

        self._kc_ws_client = WsToken(key=key,
                                     secret=secret,
                                     passphrase=passphrase,
                                     url='https://api-futures.kucoin.com')
        self._ws_public_client: KucoinFuturesWsClient | None = None

    async def _create_ws_client(self):
        # 创建ws_client
        self._ws_public_client = await KucoinFuturesWsClient.create(None, self._kc_ws_client, self._deal_kc_public_msg,
                                                                    private=False)

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
        # 创建ws_client
        await self._create_ws_client()

    async def _deal_kc_public_msg(self, msg):
        # data = msg.get('data')
        # print(msg)
        try:
            if msg.get('subject') == Subject.level2:
                level2_depth5 = market_data_parser.parse_level2_depth5(msg)
                await self._event_queue.put(Level2Depth5Event(level2_depth5))
            # elif msg.get('subject') == Subject.candleStick:
            #     bar = market_data_parser.parse_bar(msg)
            #     await self._event_queue.put(BarEvent(bar))
            else:
                self._send_msg(f"{self._strategy_name} 未知的subject {msg.get('subject')}")
                raise Exception(f"未知的subject {msg.get('subject')}")
        except Exception as e:
            self._send_msg(f"{self._strategy_name} deal_public_msg Error {str(e)}")
            await app_logger.error(f"deal_public_msg Error {str(e)}")

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _fetch_position(self, symbol, mgn_mode='isolated'):
        positions = await self._kucoinfutures_exchange.fetch_positions([symbol])
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

    async def _process_event(self):
        while True:
            try:
                event = await self._event_queue.get()
                if event.type == EventType.BAR:
                    # 处理k线
                    await self.on_bar(event.data)
                elif event.type == EventType.LEVEL2DEPTH5:
                    # 处理level2depth5
                    await self.on_level2_depth5(event.data)
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
                    params = {}
                    if co.post_only:
                        params['postOnly'] = co.post_only
                    if co.lever:
                        params['leverage'] = co.lever
                    if co.client_oid:
                        params['clientOid'] = co.client_oid
                    if co.cancel_after:
                        params['cancelAfter'] = co.cancel_after
                    if co.margin_mode:
                        params['marginMode'] = co.margin_mode

                    ret = await self._kucoinfutures_exchange.create_order(
                        symbol=co.symbol,
                        type=co.type,
                        side=co.side,
                        amount=co.size,
                        price=co.price,
                        params=params,
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

    async def _watch_binance_kline(self, symbol, kline_frequency):
        while True:
            ohlcv_list = await self._binance_exchange.watch_ohlcv(symbol, kline_frequency)
            for ohlcv in ohlcv_list:
                bar = ccxt_binance_adapter.parse_kline(ohlcv, symbol, kline_frequency)
                await self._event_queue.put(BarEvent(bar))

    async def _subscribe_level2_depth5(self, symbol):
        # topic举例 '/contractMarket/level2Depth5:XBTUSDTM'
        await self._ws_public_client.subscribe(f'/contractMarket/level2Depth5:{symbol}')

    async def _unsubscribe_level2_depth5(self, symbol):
        await self._ws_public_client.unsubscribe(f'/contractMarket/level2Depth5:{symbol}')

    async def _subscribe_positions(self, symbol):
        # TODO: 这种订阅方式，如果多次订阅可能会导致重复订阅，该问题未来需要解决
        self._position_change_task = asyncio.create_task(self._watch_positions(symbol))
        self._is_subscribe_position = True

    async def _watch_positions(self, symbol):
        while True:
            positions = await self._kucoinfutures_exchange.watch_positions(symbols=[symbol])
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
        self._kucoinfutures_markets = await self._kucoinfutures_exchange.load_markets(reload=True)

    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")

    async def on_level2_depth5(self, level2_depth5: Level2Depth5):
        raise NotImplementedError("需要实现on_order_book5")

    async def on_position(self, position_change):
        raise NotImplementedError("需要实现on_position")

    # 获取最小下单张数
    @property
    def min_contract(self):
        return self._kucoinfutures_markets[self._symbol]['limits']['amount']['min']

    # 获取每张代表多少数量的币(合约乘数)
    @property
    def contract_size(self):
        return self._kucoinfutures_markets[self._symbol]['contractSize']
