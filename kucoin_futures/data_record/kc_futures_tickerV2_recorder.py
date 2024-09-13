import asyncio
import sys
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcFuturesTickerV2Recorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=100):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._client = WsToken()
        self._ws_client = None

    def _flush_file_name(self):
        self._file_name = f"kc-futures-tickerV2-{self._symbol}-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        self._ws_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_msg, private=False)
        await self._ws_client.subscribe(f"/contractMarket/tickerV2:{self._symbol}")

    def _normalize_data(self, msg, local_ts) -> dict:
        # 返回必须含有data[]和ts字段
        data = msg.get('data')
        symbol = data.get('symbol')
        ts = data.get('ts')
        bp1 = float(data.get('bestBidPrice'))
        ap1 = float(data.get('bestAskPrice'))
        bv1 = data.get('bestBidSize')
        av1 = data.get('bestAskSize')
        return {
            "ts": ts,
            "data": [symbol, ts, local_ts] +
                    [bp1, ap1, bv1, av1]
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

    recorder = KcFuturesTickerV2Recorder(
        symbol=symbol,
        file_dir=file_dir,
        max_buffer_size=100
    )
    await recorder.run()


if __name__ == '__main__':
    asyncio.run(main())
