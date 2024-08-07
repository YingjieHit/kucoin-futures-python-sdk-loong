import asyncio
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient


async def main():
    async def deal_msg(msg):
        print(msg)
        # print(msg["data"])

    # is public
    client = WsToken()
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    # address = ('api-futures.kucoin.com',443)
    # sock.connect(address)

    ws_client = await KucoinFuturesWsClient.create(None, client, deal_msg, private=False)

    await ws_client.subscribe('/contractMarket/level2:XBTUSDM')

    # await ws_client.subscribe('/contractMarket/level3:XBTUSDM')
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

msg = {
    'topic': '/contractMarket/level2:XBTUSDM',
    'type': 'message',
    'subject': 'level2',
    'sn': 1696481133370,
    'data': {
        'sequence': 1696481133370,
        'change': '58713,sell,1066',
        'timestamp': 1720702560201
    }
}
