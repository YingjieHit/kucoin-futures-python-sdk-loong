import json
import hmac
import hashlib
import base64
import time
from uuid import uuid1
from urllib.parse import urljoin
import aiohttp

try:
    import pkg_resources
    version = 'v' + pkg_resources.get_distribution("kucoin-futures-python").version
except (ModuleNotFoundError, pkg_resources.DistributionNotFound):
    version = 'v1.0.0'


class KucoinFuturesBaseRestApiAsync(object):
    def __init__(self, key='', secret='', passphrase='', is_sandbox=False, url='', is_v1api=False):
        if url:
            self.url = url
        else:
            if is_sandbox:
               self.url = 'https://api-sandbox-futures.kucoin.com'
            else:
                self.url = 'https://api-futures.kucoin.com'
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.is_v1api = is_v1api
        # TODO: 该功能未实现
        self.TCP_NODELAY = 0

        self.base_url = "https://api-sandbox-futures.kucoin.com" if is_sandbox else "https://api-futures.kucoin.com"

    async def _request(self, method, endpoint, params=None):
        url = urljoin(self.base_url, endpoint)
        ts = str(int(time.time() * 1000))
        headers = self._create_headers(method, endpoint, ts, params)

        async with aiohttp.ClientSession() as session:
            if method in ['GET', 'DELETE']:
                async with session.request(method, url, headers=headers, params=params) as response:
                    return await response.json()
            else:
                async with session.request(method, url, headers=headers, json=params) as response:
                    return await response.json()

    def _create_headers(self, method, endpoint, timestamp, params):
        # Create pre-sign string
        pre_sign_str = timestamp + method.upper() + endpoint
        if method == 'GET' and params:
            query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
            pre_sign_str += f"?{query_string}"
        elif params:
            pre_sign_str += json.dumps(params)

        # Create signature
        signature = base64.b64encode(
            hmac.new(self.secret.encode('utf-8'), pre_sign_str.encode('utf-8'), hashlib.sha256).digest()).decode(
            'utf-8')

        # Create passphrase
        passphrase = base64.b64encode(hmac.new(self.secret.encode('utf-8'), self.passphrase.encode('utf-8'),
                                               hashlib.sha256).digest()).decode('utf-8')

        headers = {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-KEY": self.key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }

        return headers

    @property
    def return_unique_id(self):
        return ''.join([each for each in str(uuid1()).split('-')])
