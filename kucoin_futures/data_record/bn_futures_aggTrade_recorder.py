import asyncio
import sys
import json
from binance.websocket.um_futures.async_websocket_client import AsyncUMFuturesWebsocketClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcFuturesLevel2Depth5Recorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=10):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._client = AsyncUMFuturesWebsocketClient(on_message=self._deal_msg)
        
    async def _init(self):
        await self._client.start()

    def _flush_file_name(self):
        self._file_name = f"bn-futures-aggTrade-{self._symbol}-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        await self._client.agg_trade(symbol=self._symbol)

    def _normalize_data(self, msg, local_ts) -> dict|None:
        # 返回必须含有data[]和ts字段
        msg = json.loads(msg)
        if 'e' not in msg:
            return None

        symbol = msg.get('s')
        ts = msg.get('T')
        event_ts = msg.get('E')
        price = float(msg.get('p'))
        quantity = float(msg.get('q'))
        is_buyer_maker = msg.get('m')

        agg_id = msg.get('a')
        first_id = msg.get('f')
        last_id = msg.get('l')

        return {
            "ts": ts,
            "data": [symbol, ts, event_ts, local_ts] +
                    [price, quantity, is_buyer_maker] +
                    [agg_id, first_id, last_id]
        }

    @property
    def _header(self):
        return (
                ['symbol', 'ts', 'event_ts', 'local_ts'] +
                ['price', 'quantity', 'isBuyerMaker'] +
                ['aggId', 'firstId', 'lastId']
        )

async def main():
    # 读取脚本参数，第一个参数为symbol，第二个参数为目录
    symbol = sys.argv[1]
    file_dir = sys.argv[2]

    recorder = KcFuturesLevel2Depth5Recorder(
        symbol=symbol,
        file_dir=file_dir,
        max_buffer_size=10
    )
    await recorder.run()


if __name__ == '__main__':
    asyncio.run(main())
