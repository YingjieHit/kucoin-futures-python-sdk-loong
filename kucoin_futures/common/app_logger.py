import asyncio
from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from pathlib import Path


class AppLogger(object):

    def __init__(self, level='INFO', info_log_path=None, error_log_path=None):
        if info_log_path is None:
            info_log_path = 'info.log'
        if error_log_path is None:
            error_log_path = 'error.log'
        self.info_log_path = Path(info_log_path)
        self.error_log_path = Path(error_log_path)
        self.logger = Logger(level=level)  # 设置为日志级别
        self.setup_logger()

    def setup_logger(self):
        # 确保日志目录存在，如果不存在则创建
        self.info_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建并添加文件处理器
        info_handler = AsyncFileHandler(filename=str(self.info_log_path), level='INFO')
        error_handler = AsyncFileHandler(filename=str(self.error_log_path), level='ERROR')
        self.logger.add_handler(info_handler)
        self.logger.add_handler(error_handler)

    async def info(self, message):
        await self.logger.info(message)

    async def error(self, message):
        await self.logger.error(message)

    async def shutdown(self):
        await self.logger.shutdown()

async def log_sample():
    logger_manager = AppLogger('./info.log', './error.log')


    await logger_manager.info("This is an info level log.")
    await logger_manager.error("This is an error level log.")

    # 关闭logger前清理资源
    await logger_manager.shutdown()


if __name__ == '__main__':
    asyncio.run(log_sample())