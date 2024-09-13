import asyncio
import socket
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient


async def main():
    symbol = "XBTUSDTM"
    async def deal_msg(msg):
        print(msg)

    # is public
    client = WsToken()
    ws_client = await KucoinFuturesWsClient.create(None, client, deal_msg, private=False)

    await ws_client.subscribe(f"/contractMarket/execution:{symbol}")
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
