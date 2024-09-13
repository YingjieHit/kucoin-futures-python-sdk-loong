import time
import asyncio
import socket
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient



async def main():
    symbol = "BTC-USDT"
    async def deal_msg(msg):
        print(msg)

    # is public
    client = WsToken()

    ws_client = await KucoinWsClient.create(None, client, deal_msg, private=False)

    await ws_client.subscribe(f'/spotMarket/level1:{symbol}')
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


