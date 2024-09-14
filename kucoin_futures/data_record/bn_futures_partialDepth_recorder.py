import asyncio
import sys
import json
from binance.websocket.um_futures.async_websocket_client import AsyncUMFuturesWebsocketClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcFuturesPartialDepthRecorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=10, level=5, speed=100):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._level = level  # 5, 10, 20
        self._speed = speed  # 100, 250, 500
        self._client = AsyncUMFuturesWebsocketClient(on_message=self._deal_msg)

    async def _init(self):
        await self._client.start()

    def _flush_file_name(self):
        self._file_name = f"bn-futures-partialDepth{self._level}-{self._speed}ms-{self._symbol}-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        await self._client.partial_book_depth(symbol=self._symbol, level=self._level, speed=self._speed)

    def _normalize_data(self, msg, local_ts) -> dict | None:
        # 返回必须含有data[]和ts字段
        msg = json.loads(msg)
        if 'e' not in msg:
            return None

        symbol = msg.get('s')
        ts = msg.get('T')
        event_ts = msg.get('E')
        bids = msg.get('b')
        asks = msg.get('a')
        return {
            "ts": ts,
            "data": [symbol, ts, event_ts, local_ts] +
                    [float(item[0]) for item in bids] +
                    [float(item[0]) for item in asks] +
                    [float(item[1]) for item in bids] +
                    [float(item[1]) for item in asks]
        }

    @property
    def _header(self):
        return (
                ['symbol', 'ts', 'event_ts', 'local_ts'] +
                [f'bp{i}' for i in range(1, self._level + 1)] +
                [f'ap{i}' for i in range(1, self._level + 1)] +
                [f'bv{i}' for i in range(1, self._level + 1)] +
                [f'av{i}' for i in range(1, self._level + 1)]
        )


async def main():
    # 读取脚本参数，第一个参数为symbol，第二个参数为目录
    symbol = sys.argv[1]
    level = int(sys.argv[2])
    speed = int(sys.argv[3])
    file_dir = sys.argv[4]

    recorder = KcFuturesPartialDepthRecorder(
        symbol=symbol,
        file_dir=file_dir,
        max_buffer_size=10,
        level=level,
        speed=speed
    )
    await recorder.run()


if __name__ == '__main__':
    asyncio.run(main())
