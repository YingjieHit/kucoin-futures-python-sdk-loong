from kucoin_futures.common.msg_client.msg_base_client import MsgBaseClient


class PrintClient(MsgBaseClient):
    def __init__(self, chat_id=None):
        super().__init__()

    def send_msg(self, txt):
        return print(txt)