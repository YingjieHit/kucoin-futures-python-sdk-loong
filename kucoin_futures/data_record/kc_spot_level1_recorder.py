import asyncio
import sys
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcSpotLevel1Recorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=10):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._client = WsToken()
        self._ws_client = None

    def _flush_file_name(self):
        self._file_name = f"kc-spot-level1-{self._symbol}-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        self._ws_client = await KucoinWsClient.create(None, self._client, self._deal_msg, private=False)
        await self._ws_client.subscribe(f"/spotMarket/level1:{self._symbol}")

    def _normalize_data(self, msg, local_ts) -> dict:
        # 返回必须含有data[]和ts字段
        data = msg.get('data')
        bids = data.get('bids')
        asks = data.get('asks')
        ts = data.get('timestamp')
        return {
            "ts": ts,
            "data": [self._symbol, ts, local_ts] +
                    [float(bids[0]), float(asks[0]), float(bids[1]), float(asks[1])]
        }

    @property
    def _header(self):
        return (
                ['symbol', 'ts', 'local_ts'] +
                ['bp1', 'ap1', 'bv1', 'av1']
        )

async def main():
    # 读取脚本参数，第一个参数为symbol，第二个参数为目录
    symbol = sys.argv[1]
    file_dir = sys.argv[2]

    recorder = KcSpotLevel1Recorder(
        symbol=symbol,
        file_dir=file_dir,
        max_buffer_size=100
    )
    await recorder.run()


if __name__ == '__main__':
    asyncio.run(main())
