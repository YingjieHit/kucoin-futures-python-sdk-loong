import asyncio
import sys
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcFuturesTradeRecorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=10):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._client = WsToken()
        self._ws_client = None

    def _flush_file_name(self):
        self._file_name = f"{self._symbol}-trade-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        self._ws_client = await KucoinFuturesWsClient.create(None, self._client, self._deal_msg, private=False)
        await self._ws_client.subscribe(f"/contractMarket/execution:{self._symbol}")

    def _normalize_data(self, msg, local_ts) -> dict:
        # 返回必须含有data[]和ts字段
        data = msg.get('data')
        symbol = data.get('symbol')
        ts = data.get('ts')
        sequence = data.get('sequence')
        side = data.get('side')
        size = data.get('size')
        price = float(data.get('price'))
        maker_user_id = data.get('makerUserId')
        taker_order_id = data.get('takerOrderId')
        taker_user_id = data.get('takerUserId')
        maker_order_id = data.get('makerOrderId')
        trade_id = data.get('tradeId')

        return {
            "ts": ts,
            "data": [symbol, ts, local_ts] +
                    [sequence, side, size, price] +
                    [maker_user_id, taker_order_id, taker_user_id, maker_order_id, trade_id]
        }

    @property
    def _header(self):
        return (
                ['symbol', 'ts', 'local_ts'] +
                ['sequence', 'side', 'size', 'price', 'makerUserId', 'takerOrderId', 'takerUserId', 'makerOrderId', 'tradeId']
        )

async def main():
    # 读取脚本参数，第一个参数为symbol，第二个参数为目录
    symbol = sys.argv[1]
    file_dir = sys.argv[2]

    recorder = KcFuturesTradeRecorder(
        symbol=symbol,
        file_dir=file_dir,
        max_buffer_size=10
    )
    await recorder.run()


if __name__ == '__main__':
    asyncio.run(main())
