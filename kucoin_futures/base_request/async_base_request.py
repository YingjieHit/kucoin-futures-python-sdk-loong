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
        uri_path = uri
        data_json = ''
        if method in ['GET', 'DELETE']:
            if params:
                query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
                uri_path = f"{uri}?{query_string}"
        else:
            if params:
                data_json = json.dumps(params)
                uri_path += data_json

        headers = self._generate_headers(method, uri_path, auth)

        async with aiohttp.ClientSession() as session:
            async with session.request(method, urljoin(self.url, uri), headers=headers, data=data_json if method not in ['GET', 'DELETE'] else None, timeout=timeout) as response:
                return await self._check_response_data(response)

    def _generate_headers(self, method, uri_path, auth):
        headers = {"Content-Type": "application/json"}
        if auth:
            now = int(time.time() * 1000)
            str_to_sign = f"{now}{method}{uri_path}"
            sign = base64.b64encode(
                hmac.new(self.secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()).decode()

            if self.is_v1api:
                headers.update({
                    "KC-API-SIGN": sign,
                    "KC-API-TIMESTAMP": str(now),
                    "KC-API-KEY": self.key,
                    "KC-API-PASSPHRASE": self.passphrase,
                })
            else:
                passphrase = base64.b64encode(hmac.new(self.secret.encode('utf-8'), self.passphrase.encode('utf-8'),
                                                       hashlib.sha256).digest()).decode()
                headers.update({
                    "KC-API-SIGN": sign,
                    "KC-API-TIMESTAMP": str(now),
                    "KC-API-KEY": self.key,
                    "KC-API-PASSPHRASE": passphrase,
                    "KC-API-VERSION": "2",
                })
            return headers

    @staticmethod
    async def _check_response_data(response):
        if response.status == 200:
            try:
                data = await response.json()
                if data.get('code') == '200000':
                    return data.get('data', data)
                else:
                    raise Exception(f"API Error: {data.get('code')} - {data.get('msg')}")
            except ValueError:
                raise Exception(f"Non-JSON response: {await response.text()}")
        else:
            raise Exception(f"HTTP Error: {response.status} - {await response.text()}")

    @property
    def return_unique_id(self):
        return ''.join([each for each in str(uuid1()).split('-')])
