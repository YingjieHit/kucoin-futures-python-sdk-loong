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
        self._file_name = f"bn-futures-bookTicker-{self._symbol}-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        await self._client.book_ticker(symbol=self._symbol)

    def _normalize_data(self, msg, local_ts) -> dict|None:
        # 返回必须含有data[]和ts字段
        msg = json.loads(msg)
        if 'e' not in msg:
            return None

        symbol = msg.get('s')
        ts = msg.get('T')
        event_ts = msg.get('E')
        bp1 = float(msg.get('b'))
        ap1 = float(msg.get('a'))
        bv1 = float(msg.get('B'))
        av1 = float(msg.get('A'))

        return {
            "ts": ts,
            "data": [self._symbol, ts, event_ts, local_ts] +
                    [bp1, ap1, bv1, av1]
        }

    @property
    def _header(self):
        return (
                ['symbol', 'ts', 'event_ts', 'local_ts'] +
                ['bp1', 'ap1', 'bv1', 'av1']
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
