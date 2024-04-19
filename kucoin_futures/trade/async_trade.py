from kucoin_futures.base_request.async_base_request import KucoinFuturesBaseRestApiAsync


class TradeDataAsync(KucoinFuturesBaseRestApiAsync):

    async def get_fund_history(self, symbol, startAt=None, endAt=None, reverse=True, offset=0, forward=True,
                               maxCount=10):
        params = {'symbol': symbol}

        if startAt:
            params['startAt'] = startAt
        if endAt:
            params['endAt'] = endAt
        if reverse:
            params['reverse'] = reverse
        if offset:
            params['offset'] = offset
        if forward:
            params['forward'] = forward
        if maxCount:
            params['maxCount'] = maxCount

        return await self._request('GET', '/api/v1/funding-history', params=params)

    async def get_position_details(self, symbol):
        params = {'symbol': symbol}
        return await self._request('GET', '/api/v1/position', params=params)

    async def get_all_position(self):
        return await self._request('GET', '/api/v1/positions')

    async def modify_auto_deposit_margin(self, symbol, status=True):
        params = {
            'symbol': symbol,
            'status': status
        }
        return await self._request('POST', '/api/v1/position/margin/auto-deposit-status', params=params)

    async def add_margin_manually(self, symbol, margin, bizNo):
        params = {
            'symbol': symbol,
            'margin': margin,
            'bizNo': bizNo
        }
        return await self._request('POST', '/api/v1/position/margin/deposit-margin', params=params)

    async def get_contracts_risk_limit(self, symbol):
        return await self._request('GET', f'/api/v1/contracts/risk-limit/{symbol}')

    async def change_position_risk_limit_level(self, symbol, level):
        params = {
            'symbol': symbol,
            'level': level,
        }
        return await self._request('POST', '/api/v1/position/risk-limit-level/change', params=params)

    async def get_fills_details(self, symbol='', orderId='', side='', type='', startAt=None, endAt=None, **kwargs):
        params = {}
        if symbol:
            params['symbol'] = symbol
        if orderId:
            params['orderId'] = orderId
        if side:
            params['side'] = side
        if type:
            params['type'] = type
        if startAt:
            params['startAt'] = startAt
        if endAt:
            params['endAt'] = endAt
        if kwargs:
            params.update(kwargs)

        return await self._request('GET', '/api/v1/fills', params=params)

    async def get_recent_fills(self):
        return await self._request('GET', '/api/v1/recentFills')

    async def get_open_order_details(self, symbol):
        params = {
            'symbol': symbol,
        }

        return await self._request('GET', '/api/v1/openOrderStatistics', params=params)

    async def create_limit_order(self, symbol, side, lever, size, price, clientOid='', **kwargs):
        params = {
            'symbol': symbol,
            'size': size,
            'side': side,
            'price': price,
            'leverage': lever,
            'type': 'limit'
        }
        if not clientOid:
            clientOid = self.return_unique_id
        params['clientOid'] = clientOid
        if kwargs:
            params.update(kwargs)

        return await self._request('POST', '/api/v1/orders', params=params)

    async def create_market_order(self, symbol, size, side, lever, clientOid='', **kwargs):
        params = {
            'symbol': symbol,
            'size': size,
            'side': side,
            'leverage': lever,
            'type': 'market'
        }
        if not clientOid:
            clientOid = self.return_unique_id
        params['clientOid'] = clientOid
        if kwargs:
            params.update(kwargs)

        return await self._request('POST', '/api/v1/orders', params=params)

    async def create_market_maker_order(self, symbol, lever, size, price_buy, price_sell,
                                        client_oid_buy='', client_oid_sell='', post_only=True):
        params = [
            {
                'symbol': symbol,
                'size': size,
                'side': 'buy',
                'price': price_buy,
                'leverage': lever,
                'type': 'limit',
                'postOnly': post_only,
            },
            {
                'symbol': symbol,
                'size': size,
                'side': 'sell',
                'price': price_sell,
                'leverage': lever,
                'type': 'limit',
                'postOnly': post_only,
            }
        ]
        if not client_oid_buy:
            params[0]['clientOid'] = self.return_unique_id
        if not  client_oid_sell:
            params[1]['clientOid'] = self.return_unique_id

        return await self._request('POST', '/api/v1/orders/multi', params=params)

    async def cancel_order(self, orderId):
        return await self._request('DELETE', f'/api/v1/orders/{orderId}')

    async def cancel_all_limit_order(self, symbol):
        params = {
            'symbol': symbol
        }
        return await self._request('DELETE', '/api/v1/orders', params=params)

    async def cancel_all_stop_order(self, symbol):
        params = {
            'symbol': symbol
        }
        return await self._request('DELETE', '/api/v1/stopOrders', params=params)

    async def get_order_list(self, **kwargs):
        params = {}
        if kwargs:
            params.update(kwargs)

        return await self._request('GET', '/api/v1/orders', params=params)

    async def get_open_stop_order(self, **kwargs):
        params = {}
        if kwargs:
            params.update(kwargs)

        return await self._request('GET', '/api/v1/stopOrders', params=params)

    async def get_24h_done_order(self, **kwargs):
        params = {}
        if kwargs:
            params.update(kwargs)

        return await self._request('GET', '/api/v1/recentDoneOrders', params=params)

    async def get_order_details(self, orderId):
        return await self._request('GET', f'/api/v1/orders/{orderId}')

    async def get_public_funding_history(self, symbol, fr, to):
        params = {
            'symbol': symbol,
            'from': fr,
            'to': to,
        }
        return await self._request('GET', '/api/v1/contract/funding-rates', params=params)

    async def get_24h_futures_transaction_volume(self):
        return await self._request('GET', '/api/v1/trade-statistics')

    async def cancel_order_by_clientOid(self, clientOid, symbol):
        params = {
            'symbol': symbol
        }
        return await self._request('DELETE', f'/api/v1/orders/client-order/{clientOid}', params=params)
