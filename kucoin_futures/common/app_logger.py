import asyncio
from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from aiologger.levels import LogLevel
from pathlib import Path

class AppLogger(object):
    def __init__(self, info_log_path=None, error_log_path=None):
        if info_log_path is None:
            info_log_path = 'info.log'
        if error_log_path is None:
            error_log_path = 'error.log'
        self.info_log_path = Path(info_log_path)
        self.error_log_path = Path(error_log_path)

        self.info_logger = Logger(level=LogLevel.INFO)
        self.error_logger = Logger(level=LogLevel.ERROR)
        self.setup_logger()

    async def setup_logger(self):
        # 确保日志目录存在，如果不存在则创建
        self.info_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建并添加文件处理器
        info_handler = AsyncFileHandler(filename=str(self.info_log_path), mode='a')

        error_handler = AsyncFileHandler(filename=str(self.error_log_path), mode='a')

        self.info_logger.add_handler(info_handler)
        self.error_logger.add_handler(error_handler)

    async def info(self, message):
        await self.info_logger.info(message)

    async def error(self, message):
        await self.error_logger.error(message)

    async def shutdown(self):
        await self.info_logger.shutdown()
        await self.error_logger.shutdown()
