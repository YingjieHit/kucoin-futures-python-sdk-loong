import asyncio
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcFutureLevel2Depth5Recorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=10):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._client = WsToken()
        self._ws_client = None

    def _flush_file_name(self):
        raise NotImplementedError("需要实现_flush_file_name")

    # 订阅数据
    async def _subscribe_data(self):
        self._ws_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_msg, private=False)
        await self._ws_client.subscribe(f"/contractMarket/level2Depth5:{self._symbol}")

    async def _normalize_data(self, msg, local_ts) -> dict:
        # 必须含有data[]和ts字段
        raise NotImplementedError("需要实现_normalize_data")

    @property
    def _header(self):
        return ["test"]


async def main():
    recorder = KcFutureLevel2Depth5Recorder(
        symbol="XBTUSDTM",
        file_dir=""
    )

if __name__ == '__main__':
    asyncio.run(main())