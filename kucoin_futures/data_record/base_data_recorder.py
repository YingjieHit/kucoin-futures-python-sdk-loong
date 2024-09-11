import asyncio
from kucoin.comm.async_csv_writer import AsyncCsvWriter
from kucoin_futures.strategy.time_utils import time_utils
from pytscns import PyTSCNS

class BaseDataRecorder(object):
    def __init__(self, symbol, file_dir):
        self._symbol = symbol
        self._file_dir = file_dir

        self._queue = asyncio.Queue()
        self._file_name = None
        self._date_str = time_utils.get
        self._csv_writer = AsyncCsvWriter()

    async def run(self):
        await self._write_header()

        while True:
            await asyncio.sleep(60 * 60 * 24)

    async def _write_header(self):
        await self._csv_writer.write_header_if_needed(self._file_name, self._header)

    @property
    def _header(self):
        raise NotImplementedError("需要实现header")




