import asyncio
from ccxt.pro.binance import binance

from kucoin_futures.common.app_logger import app_logger
from kucoin_futures.common.msg_base_client import MsgBaseClient
from kucoin_futures.strategy.event import (EventType)


class KcFuturesBaseCta(object):
    def __init__(self, symbol, key, secret, passphrase, msg_client: MsgBaseClient | None = None,
                 strategy_name="no name"):
        self._symbol = symbol
        self._key = key
        self._secret = secret
        self._passphrase = passphrase
        self._msg_client = msg_client
        self._strategy_name = strategy_name

        self._event_queue = asyncio.Queue()

        self._process_event_task: asyncio.Task | None = None

        self._binance_exchange = binance()

    async def init(self):
        # 创建事件处理任务
        self._process_event_task = asyncio.create_task(self._process_event())

    async def _process_event(self):
        while True:
            try:
                event = await self._event_queue.get()
                if event.type == EventType.BAR:
                    # 处理k线
                    await self.on_bar(event.data)
                # elif event.type == EventType.OKX_ORDER_BOOK5:
                #     # 处理order book5
                #     await self.on_order_book5(event.data)

                # elif event.type == EventType.TRADE_ORDER:
                #     # 处理order回报
                #     await self.on_order(event.data)
                # elif event.type == EventType.POSITION_CHANGE:
                #     # 处理持仓变化
                #     await self.on_position(event.data)
            except Exception as e:
                print(f"{self._strategy_name} process_event Error {str(e)}")
                self._send_msg(f"{self._strategy_name} process_event Error {str(e)}")
                await app_logger.error(f"{self._strategy_name} process_event Error {str(e)}")

    def _send_msg(self, msg):
        if self._msg_client is not None:
            self._msg_client.send_msg(msg)

    async def on_bar(self, bar):
        raise NotImplementedError("需要实现on_bar")
