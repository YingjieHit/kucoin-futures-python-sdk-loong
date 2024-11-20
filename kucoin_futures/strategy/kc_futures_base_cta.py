import asyncio
from ccxt.pro import binance, kucoinfutures

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.strategy.enums import Subject
from kucoin_futures.strategy.market_data_parser import market_data_parser
from kucoin_futures.common.app_logger import app_logger
from kucoin_futures.common.msg_client.msg_base_client import MsgBaseClient
from kucoin_futures.strategy.event import (EventType, BarEvent, TraderOrderEvent, PositionChangeEvent,
                                           Level2Depth5Event, CreateOrderEvent, PositionSettlementEvent)
from kucoin_futures.strategy.object import MarketMakerCreateOrder, CreateOrder, CancelOrder
from kucoin_futures.trade.async_trade import TradeDataAsync
from kucoin_futures.common.external_adapter.ccxt_binance_adapter import ccxt_binance_adapter


class KcFuturesBaseCta(object):
    def __init__(self, symbol, key, secret, passphrase, msg_client: MsgBaseClient | None = None,
                 strategy_name="no name"):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase
        self._msg_client = msg_client
        self._strategy_name = strategy_name

        self._trade = TradeDataAsync(key=key, secret=secret, passphrase=passphrase)

        self._kc_futures_exchange = kucoinfutures({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
        })

        self._event_queue = asyncio.Queue()
        self._order_task_queue = asyncio.Queue()
        self._cancel_order_task_queue = asyncio.Queue()

        self._process_event_task: asyncio.Task | None = None
        self._bn_bar_task: asyncio.Task | None = None
        self._subscribe_monitor_task: asyncio.Task | None = None  # 订阅监控协程
        self._process_execute_order_task: asyncio.Task | None = None

        self._is_subscribe_level2_depth5 = False
        self._is_subscribe_bn_kline = False
        self._is_subscribe_position = False

        self._kc_futures_markets: dict | None = None

        self._binance_exchange = binance()

        self._client = WsToken(key=key,
                               secret=secret,
                               passphrase=passphrase,
                               url='https://api-futures.kucoin.com')
        self._ws_public_client: KucoinFuturesWsClient | None = None
        self._ws_private_client: KucoinFuturesWsClient | None = None

    async def init(self):
        # 读取市场信息
        await self._load_markets()
        # 创建事件处理任务
        self._process_event_task = asyncio.create_task(self._process_event())
        # 创建交易执行任务
        self._process_execute_order_task = asyncio.create_task(self._execute_order_process())
        # 创建ws_client
        await self._create_ws_client()
        # 创建订阅监控任务
        self._subscribe_monitor_task = asyncio.create_task(self._subscribe_monitoring_process())

    async def _execute_order_process(self):
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
                        await self._trade.create_market_order(co.symbol, co.size, co.side, co.lever, co.client_oid)
            except Exception as e:
                msg = f"{self._strategy_name} execute_order_process Error: {str(e)}"
                self._send_msg(msg)
                await app_logger.error(msg)

    async def _cancel_order_process(self):
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
                msg = f"{self._strategy_name} process_cancel_order Error: {str(e)}"
                self._send_msg(msg)
                await app_logger.error(msg)

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _subscribe_monitoring_process(self):
        while True:
            msg = f"{self._strategy_name} 策略正在运行"
            self._send_msg(msg)
            await asyncio.sleep(60 * 60 * 24)

    async def _fetch_position(self, symbol, mgn_mode='isolated'):
        positions = await self._kc_futures_exchange.fetch_positions([symbol])
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

    async def _create_ws_client(self):
        # 创建ws_client
        self._ws_public_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_public_msg,
                                                                    private=False)
        self._ws_private_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_private_msg,
                                                                     private=True)

    async def _deal_private_msg(self, msg):
        # data = msg.get('data')
        # print("_deal_private_msg")
        try:
            if msg.get('subject') == Subject.symbolOrderChange:
                order = market_data_parser.parse_order(msg)
                await self._event_queue.put(TraderOrderEvent(order))
            elif msg.get('subject') == Subject.positionChange:
                await self._event_queue.put(PositionChangeEvent(msg.get('data')))
            elif msg.get('subject') == Subject.positionSettlement:
                await self._event_queue.put(PositionSettlementEvent(msg.get('data')))
            else:
                self._send_msg(f"{self._strategy_name} _deal_private_msg 未知的subject: {msg}")
                print(f"_deal_private_msg 未知的subject: {msg}")
        except Exception as e:
            msg = f"""
                {self._strategy_name} _deal_private_msg error 
                Exception: {e}
                msg: {msg}
            """
            self._send_msg(msg)
            await app_logger.error(msg)

    async def _deal_public_msg(self, msg):
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
                msg = f"{self._strategy_name} _deal_public_msg 未知的subject msg: {msg}"
                self._send_msg(msg)
                raise Exception(msg)
        except Exception as e:
            msg = f"""
            {self._strategy_name} _deal_public_msg Error 
            Exception: {str(e)},
            msg: {msg}
            """
            self._send_msg(msg)
            await app_logger.error(msg)

    async def _process_event(self):
        event = None
        while True:
            try:
                event = await self._event_queue.get()
                if event.type == EventType.BAR:
                    # 处理k线
                    await self.on_bar(event.data)
                if event.type == EventType.LEVEL2DEPTH5:
                    # 处理ticker
                    await self.on_level2_depth5(event.data)

                elif event.type == EventType.TRADE_ORDER:
                    # 处理order回报
                    await self.on_order(event.data)
                elif event.type == EventType.POSITION_CHANGE:
                    # 处理持仓变化
                    await self.on_position_change(event.data)
                elif event.type == EventType.POSITION_SETTLEMENT:
                    await self.on_position_settlement(event.data)
            except Exception as e:
                msg = f"""
                    {self._strategy_name} _process_event Error 
                    event: {event}
                    Exception: {str(e)}
                """
                print(msg)
                self._send_msg(msg)
                await app_logger.error(msg)

    async def _subscribe_bn_kline(self, symbol, kline_frequency):
        if self._bn_bar_task is not None:
            self._bn_bar_task.cancel()
            self._bn_bar_task = None
        # TODO: 这里要考虑一下多周期多品种策略
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

    async def _subscribe_position_change(self, symbol):
        await self._ws_private_client.subscribe(f'/contract/position:{symbol}')
        self._is_subscribe_position = True

    async def _unsubscribe_position_change(self, symbol):
        await self._ws_private_client.unsubscribe(f'/contract/position:{symbol}')
        self._is_subscribe_position = False

    async def _subscribe_trade_orders(self, symbol):
        # topic举例 '/contractMarket/tradeOrders:XBTUSDTM'
        await self._ws_private_client.subscribe(f'/contractMarket/tradeOrders:{symbol}')

    async def _unsubscribe_trade_orders(self, symbol):
        await self._ws_private_client.unsubscribe(f'/contractMarket/tradeOrders:{symbol}')

    async def _subscribe_level2_depth5(self, symbol):
        # topic举例 '/contractMarket/level2Depth5:XBTUSDTM'
        await self._ws_public_client.subscribe(f'/contractMarket/level2Depth5:{symbol}')
        self._is_subscribe_level2_depth5 = True

    async def _unsubscribe_level2_depth5(self, symbol):
        await self._ws_public_client.unsubscribe(f'/contractMarket/level2Depth5:{symbol}')
        self._is_subscribe_level2_depth5 = False

    def _send_msg(self, msg):
        if self._msg_client is not None:
            self._msg_client.send_msg(msg)

    async def _load_markets(self):
        self._kc_futures_markets = await self._kc_futures_exchange.load_markets(reload=True)

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

    async def _cancel_all_orders(self, symbol):
        ret = await self._trade.cancel_all_limit_order(symbol)
        return ret


    def _delay_execute(self, seconds, func, *args, **kwargs):
        task = asyncio.create_task(self._delay_and_execute(seconds, func, *args, **kwargs))
        return task

    async def _delay_and_execute(self, seconds, func, *args, **kwargs):
        try:
            await asyncio.sleep(seconds)
            await func(*args, **kwargs)
        except Exception as e:
            msg = f"""
                {self._strategy_name} _delay_and_execute Error 
                Exception: {str(e)}
            """
            self._send_msg(msg)
            await app_logger.error(msg)

    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")

    async def on_level2_depth5(self, level2_depth5):
        raise NotImplementedError("需要实现on_level2_depth5")

    async def on_position_change(self, position_change):
        raise NotImplementedError("需要实现on_position_change")

    async def on_position_settlement(self, position_settlement):
        pass

    async def on_order(self, order):
        raise NotImplementedError("需要实现on_order")

    # 获取最小下单张数
    @property
    def min_contract(self):
        return self._kc_futures_markets[self._symbol]['limits']['amount']['min']

    # 获取每张代表多少数量的币(合约乘数)
    @property
    def contract_size(self):
        return self._kc_futures_markets[self._symbol]['contractSize']
