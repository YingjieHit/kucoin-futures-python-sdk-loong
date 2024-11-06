from kucoin_futures.common.msg_client.msg_base_client import MsgBaseClient
from kucoin_futures.common.msg_client.msg_client import MsgClient


class TgClient(MsgBaseClient):
    def __init__(self, telegram_info_key, feishu_key, msg_open, chat_id):
        super().__init__()
        self._chat_id = chat_id
        self._tg_client = MsgClient(telegram_info_key, feishu_key, msg_open)

    def send_msg(self, txt):
        return self._tg_client.send_msg(self._chat_id, txt)