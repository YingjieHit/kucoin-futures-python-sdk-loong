import asyncio
import sys
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from kucoin_futures.data_record.base_data_recorder import BaseDataRecorder


class KcSpotTradeRecorder(BaseDataRecorder):
    def __init__(self, symbol, file_dir, max_buffer_size=10):
        super().__init__(symbol, file_dir, max_buffer_size)
        self._client = WsToken()
        self._ws_client = None

    def _flush_file_name(self):
        self._file_name = f"kc-spot-trade-{self._symbol}-{self._cur_date_str}.csv"

    # 订阅数据
    async def _subscribe_data(self):
        self._ws_client = await KucoinWsClient.create(None, self._client, self._deal_msg, private=False)
        await self._ws_client.subscribe(f"/market/match:{self._symbol}")

    def _normalize_data(self, msg, local_ts) -> dict:
        # 返回必须含有data[]和ts字段
        data = msg.get('data')
        symbol = data.get('symbol')
        ts = int(data.get('time'))
        sequence = data.get('sequence')
        side = data.get('side')
        size = float(data.get('size'))
        price = float(data.get('price'))
        taker_order_id = data.get('takerOrderId')
        maker_order_id = data.get('makerOrderId')
        trade_id = data.get('tradeId')
        _type = data.get('type')

        return {
            "ts": ts,
            "data": [symbol, ts, local_ts] +
                    [sequence, side, size, price] +
                    [taker_order_id, maker_order_id, trade_id, _type]
        }

    @property
    def _header(self):
        return (
                ['symbol', 'ts', 'local_ts'] +
                ['sequence', 'side', 'size', 'price', 'takerOrderId', 'makerOrderId', 'tradeId', 'type']
        )


async def main():
    # 读取脚本参数，第一个参数为symbol，第二个参数为目录
    symbol = sys.argv[1]
    file_dir = sys.argv[2]

    recorder = KcSpotTradeRecorder(
        symbol=symbol,
        file_dir=file_dir,
        max_buffer_size=10
    )
    await recorder.run()


if __name__ == '__main__':
    asyncio.run(main())
