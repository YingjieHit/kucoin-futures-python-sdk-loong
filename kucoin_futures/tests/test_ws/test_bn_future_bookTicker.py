import asyncio
import json
from binance.websocket.um_futures.async_websocket_client import AsyncUMFuturesWebsocketClient


async def main():
    symbol = 'BTCUSDT'
    async def deal_public_msg(msg):
        msg = json.loads(msg)
        if 'e' in msg:
            print(msg)

    bn_client = AsyncUMFuturesWebsocketClient(on_message=deal_public_msg)
    await bn_client.start()
    await bn_client.book_ticker(symbol)

    while True:
        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())


