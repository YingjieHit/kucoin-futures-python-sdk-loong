import asyncio
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcFuturesLevel2Depth5Recorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=10):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._client = WsToken()
        self._ws_client = None

    def _flush_file_name(self):
        return f"{self._symbol}_level2Depth5-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        self._ws_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_msg, private=False)
        await self._ws_client.subscribe(f"/contractMarket/level2Depth5:{self._symbol}")

    def _normalize_data(self, msg, local_ts) -> dict:
        # 返回必须含有data[]和ts字段
        data = msg.get('data')
        bids = data.get('bids')
        asks = data.get('asks')
        ts = data.get('ts')
        return {
            "ts": ts,
            "data": [self._symbol, ts, local_ts] +
                    [float(item[0]) for item in bids] +
                    [float(item[0]) for item in asks] +
                    [item[1] for item in bids] +
                    [item[1] for item in asks]
        }

    @property
    def _header(self):
        return (
                ['symbol', 'ts', 'local_ts'] +
                [f'bp{i}' for i in range(5)] +
                [f'ap{i}' for i in range(5)] +
                [f'bv{i}' for i in range(5)] +
                [f'av{i}' for i in range(5)]
        )

async def main():
    recorder = KcFuturesLevel2Depth5Recorder(
        symbol="XBTUSDTM",
        file_dir="/home/ec2-user/HFT_data/KucoinFuture/level2Depth5",
        max_buffer_size=10
    )
    await recorder.run()


if __name__ == '__main__':
    asyncio.run(main())
