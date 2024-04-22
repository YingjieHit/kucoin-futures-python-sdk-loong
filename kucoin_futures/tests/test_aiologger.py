import asyncio
from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from aiologger.levels import LogLevel

async def main():
    # 创建一个日志器
    logger = Logger(level=LogLevel.DEBUG)

    # 创建一个异步文件处理器
    log_file_path = "your_log_file.log"  # 指定日志文件的路径
    file_handler = AsyncFileHandler(filename=log_file_path, mode='a')

    # 将文件处理器添加到日志器
    logger.add_handler(file_handler)

    await file_handler.close()
    logger.remove_handler(file_handler)

    # 记录一些日志信息
    await logger.debug("这是一条debug信息")
    await logger.info("这是一条info信息")
    await logger.warning("这是一条warning信息")
    await logger.error("这是一条error信息")
    await logger.critical("这是一条critical信息")

    # 确保所有日志已经写入，然后关闭日志器
    await logger.shutdown()

# 运行异步主函数
asyncio.run(main())
