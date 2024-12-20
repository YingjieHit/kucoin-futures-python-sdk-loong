import json

from binance.websocket.cm_futures.async_websocket_client import AsyncCMFuturesWebsocketClient
from binance.websocket.async_websocket_client import AsyncWebsocketClient as BnWsClient
from kucoin_futures.strategy.enums import Subject
from kucoin_futures.common.msg_client.msg_base_client import MsgBaseClient
from kucoin_futures.strategy.market_data_parser import market_data_parser
from kucoin_futures.strategy.event import (Level2Depth5Event, BarEvent)
from kucoin_futures.strategy.base_cta import BaseCta
from kucoin_futures.common.const import KC_TO_BN_SYMBOL, KC_TO_BN_FREQUENCY
from kucoin_futures.common.app_logger import app_logger


class BaseCmCta(BaseCta):
    def __init__(self, symbol, key, secret, passphrase, msg_client: MsgBaseClient | None = None,
                 strategy_name="no name"):
        super().__init__(symbol, key, secret, passphrase, msg_client, strategy_name)
        self._bn_client = AsyncCMFuturesWebsocketClient(on_message=self._deal_public_msg)
        self._is_subscribe_bn_kline = False

    async def _deal_public_msg(self, msg: dict|str):
        try:
            if isinstance(msg, str):
                msg = json.loads(msg)
            # KC接口
            if 'subject' in msg:
                subject = msg.get('subject')
                if subject == Subject.level2:
                    level2_depth5 = market_data_parser.parse_level2_depth5(msg)
                    await self._event_queue.put(Level2Depth5Event(level2_depth5))
                elif subject == Subject.candleStick:
                    bar = market_data_parser.parse_bar(msg)
                    await self._event_queue.put(BarEvent(bar))
                else:
                    msg = f"{self._strategy_name}未订阅的subject {msg}"
                    self._send_msg(msg)
                    print(msg)
            # BN接口
            elif 'e' in msg:
                e = msg.get('e')
                if e == 'kline':
                    bar = market_data_parser.parse_bn_bar(msg)
                    await self._event_queue.put(BarEvent(bar))
                else:
                    msg = f"{self._strategy_name}未订阅的e {msg}"
                    self._send_msg(msg)
                    print(msg)
            else:
                msg = f"{self._strategy_name}未知的msg {msg}"
                self._send_msg(msg)
                print(msg)
        except Exception as e:
            msg = f"{self._strategy_name} deal_public_msg Error {str(e)}"
            self._send_msg(msg)
            print(msg)
            await app_logger.error(msg)

    async def init(self):
        await super().init()
        await self._bn_client.start()

    async def _subscribe_bn_kline(self, symbol, kline_frequency):
        symbol = KC_TO_BN_SYMBOL[symbol]
        interval = KC_TO_BN_FREQUENCY[kline_frequency]
        await self._bn_client.kline(symbol, interval)
        self._is_subscribe_bn_kline = True

    async def _unsubscribe_bn_kline(self, symbol, kline_frequency):
        symbol = KC_TO_BN_SYMBOL[symbol]
        interval = KC_TO_BN_FREQUENCY[kline_frequency]
        await self._bn_client.kline(symbol, interval, action=BnWsClient.ACTION_UNSUBSCRIBE)
        self._is_subscribe_bn_kline = False


