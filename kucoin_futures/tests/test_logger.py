import asyncio
from kucoin_futures.common.app_logger import AppLogger



async def main():
    logger = AppLogger()
    print(1)
    await logger.info("aaaaa")
    await logger.info("bbbbb")
    await logger.error("12345")



if __name__ == '__main__':
    asyncio.run(main())
