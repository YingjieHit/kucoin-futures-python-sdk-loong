import asyncio
import json
import hmac
import hashlib
import base64
import time
from uuid import uuid1
from urllib.parse import urljoin
import aiohttp


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

    async def _request(self, method, uri, timeout=5, auth=True, params=None):
        pass



















