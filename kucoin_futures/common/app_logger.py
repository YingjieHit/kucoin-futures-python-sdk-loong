import asyncio
from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from pathlib import Path


# 创建一个应用的日志类
class AppLogger(object):
    # 初始化方法，传入日志级别，日志文件路径，错误日志文件路径
    def __init__(self, level='INFO', info_log_path=None, error_log_path=None):
        if info_log_path is None:
            info_log_path = 'info.log'
        if error_log_path is None:
            error_log_path = 'error.log'
        self.info_log_path = Path(info_log_path)
        self.error_log_path = Path(error_log_path)
        self.logger = Logger(level=level)  # 设置为日志级别
        self.setup_logger()
    
    # 设置日志
    def setup_logger(self):
        # 设置info日志
        print(self.info_log_path)
        print(type(self.info_log_path))
        # info_log_handler = AsyncFileHandler(self.info_log_path)
        # self.logger.addHandler(info_log_handler)
        # # 设置error日志
        # error_log_handler = AsyncFileHandler(self.error_log_path)
        # self.logger.addHandler(error_log_handler)

    # info日志
    async def info(self, msg):
        await self.logger.info(msg)

    # error日志
    async def error(self, msg):
        await self.logger.error(msg)
    
    # 关闭日志
    async def shutdown(self):
        await self.logger.shutdown()


