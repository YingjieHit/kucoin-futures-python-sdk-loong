import asyncio

from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.strategy.enums import Subject


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
        self._ws_public_client: KucoinFuturesWsClient|None = None
        self._ws_private_client: KucoinFuturesWsClient|None = None
        self._ws_enable = False
        asyncio.create_task(self._create_ws_client())
        while not self._ws_enable:
            pass



    async def _create_ws_client(self):
        print(1)
        # 创建ws_client
        self._ws_public_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_public_msg,
                                                                   private=False)
        self._ws_private_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_private_msg,
                                                                    private=True)
        self._ws_enable = True

    async def run(self):
        raise NotImplementedError("需要实现run")

    async def _deal_public_msg(self, msg):
        data = msg.get('data')
        print(msg)
        # if msg.get('subject') == Subject.tickerV2:
        #     ticker = utils.dict_2_ticker(data)
        #     await self.event_queue.put(TickerEvent(ticker))

    async def _deal_private_msg(self, msg):
        data = msg.get('data')



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




