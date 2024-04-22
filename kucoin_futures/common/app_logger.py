import asyncio
from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from pathlib import Path

class AsyncLogger(object):
    def __init__(self, level='DEBUG', info_log_path=None, error_log_path=None):
        self.info_log_path = Path(info_log_path)
        self.error_log_path = Path(error_log_path)
        self.logger = Logger(level='level') 

    async def setup_logger(self):
        # 确保日志目录存在，如果不存在则创建
        self.info_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建并添加文件处理器
        info_handler = AsyncFileHandler(filename=str(self.info_log_path))
        info_handler.level = 'INFO'

        error_handler = AsyncFileHandler(filename=str(self.error_log_path))
        error_handler.level = 'ERROR'

        self.logger.add_handler(info_handler)
        self.logger.add_handler(error_handler)

    async def log_info(self, message):
        await self.logger.info(message)

    async def log_error(self, message):
        await self.logger.error(message)

    async def shutdown(self):
        await self.logger.shutdown()

async def log_sample():
    logger_manager = AsyncLogger('/path/to/your/logs/info.log', '/path/to/your/logs/error.log')
    await logger_manager.setup_logger()

    await logger_manager.log_info("This is an info level log.")
    await logger_manager.log_error("This is an error level log.")

    # 关闭logger前清理资源
    await logger_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(log_sample())
