import time
import asyncio
import socket
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient



async def main():
    symbol = "BTC-USDT"
    async def deal_msg(msg):
        # print(msg)
        data = msg.get('data')
        symbol = data.get('symbol')
        ts = data.get('time')
        sequence = data.get('sequence')
        side = data.get('side')
        size = float(data.get('size'))
        price = float(data.get('price'))
        taker_order_id = data.get('takerOrderId')
        maker_order_id = data.get('makerOrderId')
        trade_id = data.get('tradeId')
        _type = data.get('type')

        print(
            [symbol, ts, sequence, side, size, price, taker_order_id, maker_order_id, trade_id, _type])

    # is public
    client = WsToken()

    ws_client = await KucoinWsClient.create(None, client, deal_msg, private=False)

    await ws_client.subscribe(f'/market/match:{symbol}')
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


