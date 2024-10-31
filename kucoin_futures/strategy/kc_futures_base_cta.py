import asyncio
from ccxt.pro import binance, kucoinfutures

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.strategy.enums import Subject
from kucoin_futures.strategy.market_data_parser import market_data_parser
from kucoin_futures.common.app_logger import app_logger
from kucoin_futures.common.msg_base_client import MsgBaseClient
from kucoin_futures.strategy.event import (EventType, BarEvent, TraderOrderEvent, PositionChangeEvent,
                                           Level2Depth5Event)
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

        self._kc_futures_exchange = kucoinfutures({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
        })

        self._event_queue = asyncio.Queue()

        self._process_event_task: asyncio.Task | None = None
        self._bn_bar_task: asyncio.Task | None = None

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
        # 创建ws_client
        await self._create_ws_client()

    async def _create_ws_client(self):
        # 创建ws_client
        self._ws_public_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_public_msg,
                                                                    private=False)
        self._ws_private_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_private_msg,
                                                                     private=True)

    async def _deal_private_msg(self, msg):
        # data = msg.get('data')
        # print("_deal_private_msg")
        # print(msg)
        try:
            if msg.get('subject') == Subject.symbolOrderChange:
                order = market_data_parser.parse_order(msg)
                await self._event_queue.put(TraderOrderEvent(order))
            elif msg.get('subject') == Subject.positionChange:
                await self._event_queue.put(PositionChangeEvent(msg.get('data')))
            else:
                self._send_msg(f"{self._strategy_name} _deal_private_msg 未知的subject: {msg.get('subject')}")
                print(f"_deal_private_msg 未知的subject: {msg.get('subject')}")
        except Exception as e:
            self._send_msg(f"_deal_private_msg Error {str(e)}")
            await app_logger.error(f"_deal_private_msg Error {str(e)}")

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
                self._send_msg(f"{self._strategy_name} 未知的subject {msg.get('subject')}")
                raise Exception(f"未知的subject {msg.get('subject')}")
        except Exception as e:
            self._send_msg(f"deal_public_msg Error {str(e)}")
            await app_logger.error(f"deal_public_msg Error {str(e)}")

    async def _process_event(self):
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
            except Exception as e:
                print(f"{self._strategy_name} process_event Error {str(e)}")
                self._send_msg(f"{self._strategy_name} process_event Error {str(e)}")
                await app_logger.error(f"{self._strategy_name} process_event Error {str(e)}")

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

    async def _subscribe_position(self, symbol):
        await self._ws_private_client.subscribe(f'/contract/position:{symbol}')

    async def _unsubscribe_position(self, symbol):
        await self._ws_private_client.unsubscribe(f'/contract/position:{symbol}')

    def _send_msg(self, msg):
        if self._msg_client is not None:
            self._msg_client.send_msg(msg)

    async def _load_markets(self):
        self._kc_futures_markets = await self._kc_futures_exchange.load_markets(reload=True)

    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")

    async def on_level2_depth5(self, level2_depth5):
        raise NotImplementedError("需要实现on_level2_depth5")

    async def on_position_change(self, position_change):
        raise NotImplementedError("需要实现on_position_change")

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
