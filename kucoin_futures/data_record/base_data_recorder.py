import asyncio
import os
from kucoin.comm.async_csv_writer import AsyncCsvWriter
from kucoin_futures.strategy.time_utils import time_utils
from pytscns import PyTSCNS

class BaseDataRecorder(object):
    def __init__(self, symbol, file_dir, max_buffer_size=10):
        self._symbol = symbol
        self._file_dir = file_dir
        self._max_buffer_size = max_buffer_size

        self._file_name: str = ''
        self._cur_date_str: str = ''  # 当前日期
        self._file_path: str = ''  # 文件路径
        self._queue = asyncio.Queue()
        self._csv_writer = AsyncCsvWriter()

        self._tscns = PyTSCNS()
        self._tscns_calibrate_task = None

        self._data_buffer = []
        self._data_record_task = None

    async def run(self):
        # 确认存在目录
        self._confirm_dir()
        # 开启时间校准协程
        self._tscns_calibrate_task = asyncio.create_task(self._tscns_calibrate_process())
        # 开启存储数据协程
        self._data_record_task = asyncio.create_task(self._data_record_process())
        # 订阅数据
        await self._subscribe_data()

        while True:
            await asyncio.sleep(60 * 60 * 24)

    # 确认存在目录，如果不存在则创建
    def _confirm_dir(self):
        if not os.path.exists(self._file_dir):
            os.makedirs(self._file_dir)  # 递归创建文件夹

    async def _write_header(self):
        await self._csv_writer.write_header_if_needed(self._file_path, self._header)

    async def _deal_msg(self, msg):
        # 1. 记录本地时间戳
        local_ts = str(self._tscns.rdns()) + '\t'
        # 2. 数据标准化
        data = self._normalize_data(msg, local_ts)
        # 3. 数据放入消息队列
        await self._queue.put(data)

    # tscns校准函数
    async def _tscns_calibrate_process(self):
        while True:
            await asyncio.sleep(2)
            self._tscns.calibrate()

    async def _data_record_process(self):
        while True:
            try:
                msg: dict = await self._queue.get()
                data = msg.get('data')
                ts = msg.get('ts')

                # 检查是否跨日,跨日则把缓存写入文件
                date_str = time_utils.get_date_str_from_ts(ts)
                if date_str != self._cur_date_str:
                    # 如果队列中有数据，先清空队列
                    if self._data_buffer:
                        await self._flush_data_to_file()
                    # 更新当前日期
                    self._cur_date_str = date_str
                    # 更新当前存储path
                    self._flush_file_path()
                    # 创建新的文件
                    await self._write_header()

                # 将数据写入缓存
                self._data_buffer.append(data)
                # 缓存是到阈值则存入数据
                if len(self._data_buffer) >= self._max_buffer_size:
                    await self._flush_data_to_file()

            except Exception as e:
                print(f"_data_record_process error", e)

    # 存储数据，清空buffer
    async def _flush_data_to_file(self):
        if self._data_buffer:
            await self._csv_writer.write_rows(self._data_buffer, self._file_path)
            self._data_buffer.clear()

    def _flush_file_path(self):
        self._flush_file_name()
        print(f"flush file path: {self._file_path}")
        print(f"flush file name: {self._file_name}")
        print(f"flush file dir: {self._file_dir}")
        self._file_path = os.path.join(self._file_dir, self._file_name)

    def _flush_file_name(self):
        raise NotImplementedError("需要实现_flush_file_name")

    # 订阅数据
    async def _subscribe_data(self):
        raise NotImplementedError("需要实现_subscribe_data")

    def _normalize_data(self, msg, local_ts) -> dict:
        # 必须含有data[]和ts字段
        raise NotImplementedError("需要实现_normalize_data")

    @property
    def _header(self):
        raise NotImplementedError("需要实现_header")
