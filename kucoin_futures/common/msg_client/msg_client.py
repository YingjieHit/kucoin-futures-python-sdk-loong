import requests
import json

class MsgClient:
    def __init__(self, telegram_info_key, feishu_key, msg_open):
        self.service_url = f'https://api.telegram.org/bot{telegram_info_key}/sendMessage'
        self.feishu_url = f'https://open.feishu.cn/open-apis/bot/v2/hook/{feishu_key}'
        self.msg_open = msg_open

    def send_feishu(self, txt="wake up,some bad things happen"):
        payload_message = {"msg_type": "text", "content": {"text": txt}}
        headers = {'Content-Type': 'application/json'}
        r = requests.request("POST", self.feishu_url, headers=headers, data=json.dumps(payload_message))
        # print(r)
        return r

    def send_msg(self, chat_id, txt):
        if not self.msg_open:
            return True, ""
        payload = {'chat_id': chat_id, 'text': txt}  # info
        r = requests.post(self.service_url, data=payload)
        if '"ok":false' in r.text:
            msg = f"""
                send msg to telegram error, 
                msg: {txt},
                r.text: {r.text} 
            """
            self.send_feishu(msg)  # telegram发不出消息的情况
            return False, r.text
        return True, ""

    def send_html(self, chat_id, txt):
        if not self.msg_open:
            return True, ""
        payload = {'chat_id': chat_id, 'text': txt, 'parse_mode': 'HTML'}  # info
        r = requests.post(self.service_url, data=payload)
        if '"ok":false' in r.text:
            print(r.text)
            self.send_feishu()  # telegram发不出消息的情况
            return False, r.text
        return True, ""

    def send_info(self, txt):
        return self.send_msg("-1002064536264", txt)

    def send_warning(self, txt):
        return self.send_msg("-1002124841029", txt)

    def send_html_info(self, txt, is_release=True):
        if is_release:
            return self.send_html("-1002064536264", txt)
        else:
            # 预览群组
            return self.send_html("-4105427840", txt)

    def send_normal_html(self, txt):
        return self.send_html("-4185188977", txt)

    def send_gtp(self, txt):
        '''send to GrantTrump'''
        return self.send_html("6506330009", txt)
        # return self.send_msg("6506330009",txt)


if __name__ == "__main__":
    client = MsgClient()
    # client.send_warning("test warning")
    # client.send_normal_html("test")
    client.send_msg("-4535086069", "test")  # 群
    # # client.send_feishu()
    # client.send_gtp("test")
    # client.send_info("test info")
