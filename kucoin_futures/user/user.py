from kucoin_futures.base_request.base_request import KucoinFuturesBaseRestApi


class UserData(KucoinFuturesBaseRestApi):

    def transfer_kucoin_account(self, amount, bizNo=''):
        """
        https://docs.kumex.com/#transfer-funds-to-kucoin-main-account
        :param bizNo:  (Mandatory) A unique ID generated by the user, to ensure the operation is processed by the system only once.
            You are suggested to use UUID
        :type: str
        :param amount: (Mandatory) Amount to be transfered out
        :type:float
        :return:
        {
            "applyId": "5bffb63303aa675e8bbe18f9" //Transfer-out request ID
        }
        """
        params = {'amount': amount}
        if not bizNo:
            bizNo = self.return_unique_id[0:23]
        params['bizNo'] = bizNo
        return self._request('POST', '/api/v1/transfer-out', params=params)

    def transfer_kucoin_account_v2(self, amount, bizNo=''):
        """
        https://docs.kumex.com/#transfer-funds-to-kucoin-main-account-2
        :param bizNo:  (Mandatory) A unique ID generated by the user, to ensure the operation is processed by the system only once.
            You are suggested to use UUID
        :type: str
        :param amount: (Mandatory) Amount to be transfered out
        :type:float
        :return:
        {
            "applyId": "5bffb63303aa675e8bbe18f9" //Transfer-out request ID
        }
        """
        params = {'amount': amount}
        if not bizNo:
            bizNo = self.return_unique_id[0:23]
        params['bizNo'] = bizNo
        return self._request('POST', '/api/v2/transfer-out', params=params)
    
    def transfer_kucoin_account_v3(self, amount, currency, recAccountType):
        """
        https://docs.kucoin.com/futures/#transfer-funds-to-kucoin-main-account-or-kucoin-trade-account
        :param amount: (Mandatory) Amount to be transfered out
        :type:float
        :param currency: (Mandatory) Currency, including XBT,USDT
        :type:str
        :param recAccountType: (Mandatory) Receive account type, including MAIN,TRADE
        :type:str
        :return:
                {
                    "applyId": "625e542ad1169d000122f2d8",
                    "bizNo": "625e542ad1169d000122f2d7",
                    "payAccountType": "CONTRACT",
                    "payTag": "DEFAULT",
                    "remark": "",
                    "recAccountType": "MAIN",
                    "recTag": "DEFAULT",
                    "recRemark": "",
                    "recSystem": "KUCOIN",
                    "status": "PROCESSING",
                    "currency": "USDT",
                    "amount": "0.001",
                    "fee": "0",
                    "sn": 889048789592893,
                    "reason": "",
                    "createdAt": 1650349098000,
                    "updatedAt": 1650349098000
                }
        """
        params = {'amount': amount, 'currency': currency, 'recAccountType':recAccountType}
        return self._request('POST', '/api/v3/transfer-out', params=params)
    
    def transfer_funds_to_futures_account(self,amount, currency, payAccountType):
        """
        https://docs.kucoin.com/futures/#transfer-funds-to-kucoin-futures-account
        :param amount: (Mandatory) Amount to be transfered out
        :type:float
        :param currency: (Mandatory) Currency, including XBT,USDT
        :type:str
        :param payAccountType: (Mandatory) Payment account type, including MAIN,TRADE
        :type:str
        :return:
                {
                    "code": "200000",
                    "data": null
                }
        """
        params = {'amount': amount, 'currency': currency, 'payAccountType':payAccountType}
        return self._request('POST', '/api/v1/transfer-in', params=params)

    def get_Transfer_history(self, **kwargs):
        """
        https://docs.kumex.com/#get-transfer-out-request-records-2
        :param kwargs:  [optional]  status,  startAt, endAt, currentPage , pageSize  and so on
        :return: {'totalNum': 0, 'totalPage': 0, 'pageSize': 50, 'currentPage': 1, 'items': [{
        "applyId": "5cd53be30c19fc3754b60928", //Transfer-out request ID
        "currency": "XBT", //Currency
        "status": "SUCCESS", //Status  PROCESSING, SUCCESS, FAILURE
        "amount": "0.01", //Transaction amount
        "reason": "", //Reason caused the failure
        "offset": 31986850860000, //Offset
        "createdAt": 1557769977000 //Request application time}, ....]}
        """
        params = {}
        if kwargs:
            params.update(kwargs)
        return self._request('GET', '/api/v1/transfer-list', params=params)

    def cancel_Transfer_out(self, applyId):
        """
        https://docs.kumex.com/#cancel-transfer-out-request
        :param applyId: (Mandatory) Transfer ID (Initiate to cancel the transfer-out request)
        :return: {'code': '200000',"data": {
       "applyId": "5bffb63303aa675e8bbe18f9" //Transfer-out request ID
        }  }
        """
        return self._request('DELETE', '/api/v1/cancel/transfer-out?applyId={}'.format(applyId))

    def get_withdrawal_quota(self, currency):
        """
        https://docs.kumex.com/#get-withdrawal-limit
        :param currency:  XBT  str (Mandatory)
        :return:
        {
          "currency": "XBT",//Currency
          "limitAmount": 2,//24h withdrawal limit
          "usedAmount": 0,//Withdrawal amount over the past 24h.
          "remainAmount": 2,//24h available withdrawal amount
          "availableAmount": 99.89993052,//Available balance
          "withdrawMinFee": 0.0005,//Withdrawal fee charges
          "innerWithdrawMinFee": 0,//Inner withdrawal fee charges
          "withdrawMinSize": 0.002,//Min. withdrawal amount
          "isWithdrawEnabled": true,//Available to withdrawal or not
          "precision": 8//Precision of the withdrawal amount
        }
        """
        params = {
            'currency': currency
        }
        return self._request('GET', '/api/v1/withdrawals/quotas', params=params)

    def sand_withdrawal(self, currency, address, amount, **kwargs):
        """
        https://docs.kumex.com/#withdraw-funds
        :param currency: Currency, only Bitcoin (XBT) is currently supported. (Mandatory)
        :type: str
        :param address: 	Withdrawal address (Mandatory)
        :type: str
        :param amount: Withdrawal amount (Mandatory)
        :type: float
        :param kwargs:  [Optional]  isInner, remark
        :return:
         {
            "withdrawalId": "" // Withdrawal ID. This ID can be used to cancel the withdrawal
        }
        """
        params = {
            'currency': currency,
            'address': address,
            'amount': amount
        }
        if kwargs:
            params.update(kwargs)

        return self._request('POST', '/api/v1/withdrawals', params=params)

    def get_withdrawal_list(self, **kwargs):
        """
        https://docs.kumex.com/#get-withdrawal-list
        :param kwargs: [optional] currentPage , pageSize  and so on
        :return:
         {
              "currentPage": 1,
              "pageSize": 50,
              "totalNum": 10,
              "totalPage": 1,
              "items": [{
                "withdrawalId": "5cda659603aa67131f305f7e",//Withdrawal ID. This ID can be used to cancel the withdrawal
                "currency": "XBT",//Currency
                "status": "FAILURE",//Status
                "address": "3JaG3ReoZCtLcqszxMEvktBn7xZdU9gaoJ",//Withdrawal address
                "isInner": true,//Inner withdrawal or not
                "amount": 1,//Withdrawal amount
                "fee": 0,//Withdrawal fee charges
                "walletTxId": "",//Wallet TXID
                "createdAt": 1557816726000,//Withdrawal time
                "remark": "",//Withdrawal remarks
                "reason": "Assets freezing failed."// Reason causing the failure
          }]
        }
        """
        params = {}
        if kwargs:
            params.update(kwargs)

        return self._request('GET', '/api/v1/withdrawal-list', params=params)

    def cancel_withdrawal(self, withdrawalId):
        """
        https://docs.kumex.com/#cancel-withdrawal
        :param withdrawalId: Path Parameter. Withdrawal ID  (Mandatory)
        :type: str
        :return: {'address': '', 'memo': ''}
        """
        return self._request('DELETE', '/api/v1/withdrawals/{withdrawalId}'.format(withdrawalId=withdrawalId))

    def get_deposit_address(self, currency):
        """
        https://docs.kumex.com/#get-deposit-address
        :param currency:  XBT  str (Mandatory)
        :return:
        """
        params = {
            'currency': currency
        }
        return self._request('GET', '/api/v1/deposit-address', params=params)

    def get_deposit_list(self, **kwargs):
        """
        https://docs.kumex.com/#get-deposits-list

        :param kwargs:  [optional]  currentPage , pageSize  and so on
        :return:
            {
              "currentPage": 1,
              "pageSize": 50,
              "totalNum": 1,
              "totalPage": 1,
              "items": [{
                "currency": "XBT",//Currency
                "status": "SUCCESS",//Status type: PROCESSING, WALLET_PROCESSING, SUCCESS, FAILURE
                "address": "5CD018972914B66104BF8842",//Deposit address
                "isInner": false,//Inner transfer or not
                "amount": 1,//Deposit amount
                "fee": 0,//Fees for deposit
                "walletTxId": "5CD018972914B66104BF8842",//Wallet TXID
                "createdAt": 1557141673000 //Funds deposit time
              }]
            }

        """
        params = {}
        if kwargs:
            params.update(kwargs)

        return self._request('GET', '/api/v1/deposit-list', params=params)

    def get_account_overview(self, currency='XBT'):
        """
        https://docs.kumex.com/#get-account-overview
        :return:
        {
          "accountEquity": 99.8999305281, //Account equity
          "unrealisedPNL": 0, //Unrealised profit and loss
          "marginBalance": 99.8999305281, //Margin balance
          "positionMargin": 0, //Position margin
          "orderMargin": 0, //Order margin
          "frozenFunds": 0, //Frozen funds for withdrawal and out-transfer
          "availableBalance": 99.8999305281 //Available balance
          "currency": "XBT" //currency code
        }
        """
        params = {
            'currency': currency
        }
        return self._request('GET', '/api/v1/account-overview', params=params)

    def get_transaction_history(self, **kwargs):
        """
        https://docs.kumex.com/#get-transaction-history
        :param kwargs: [optional]  startAt, endAt, type, offset maxCount
        :return:
         {
          "hasMore": false,//Whether there are more pages
          "dataList": [{
            "time": 1558596284040, //Event time
            "type": "RealisedPNL", //Type
            "amount": 0, //Transaction amount
            "fee": null,//Fees
            "accountEquity": 8060.7899305281, //Account equity
            "status": "Pending", //Status. If you have held a position in the current 8-hour settlement period.
            "remark": "XBTUSDM",//Ticker symbol of the contract
            "offset": -1 //Offset,
            "currency": "XBT"  //Currency
          },
          {
            "time": 1557997200000,
            "type": "RealisedPNL",
            "amount": -0.000017105,
            "fee": 0,
            "accountEquity": 8060.7899305281,
            "status": "Completed",//Status. Status. Funding period that has been settled.
         "remark": "XBTUSDM",
         "offset": 1,
         "currency": "XBT"  //Currency
         }]
        }
        """
        params = {}
        if kwargs:
            params.update(kwargs)

        return self._request('GET', '/api/v1/transaction-history', params=params)

    def get_sub_account_api_list(self, sub_name, **kwargs):
        """
        https://docs.kucoin.com/futures/#get-sub-account-futures-api-list
        :param sub_name: Sub-account name.
        :type: str
        :param kwargs: [optional] apiKey
        :return:
        {
            "subName": "AAAAAAAAAAAAA0022",
            "remark": "hytest01-01",
            "apiKey": "63032453e75087000182982b",
            "permission": "General",
            "ipWhitelist": "",
            "createdAt": 1661150291000
        }
        """
        params = {
            'subName': sub_name
        }
        if kwargs:
            params.update(kwargs)
        return self._request('GET', '/api/v1/sub/api-key', params=params)

    def create_apis_for_sub_account(self, sub_name, passphrase, remark, **kwargs):
        """
        https://docs.kucoin.com/futures/#create-futures-apis-for-sub-account
        :param sub_name: Sub-account name(must contain 7-32 characters, at least one number and one letter. Cannot contain any spaces.)
        :type: str
        :param passphrase: Password(Must contain 7-32 characters. Cannot contain any spaces.)
        :type: str
        :param remark: Remarks(1~24 characters)
        :type: str
        :param kwargs:  [Optional]  permission, ipWhitelist, expire
        :return:
         {
            "subName": "AAAAAAAAAA0007",
            "remark": "remark",
            "apiKey": "630325e0e750870001829864",
            "apiSecret": "110f31fc-61c5-4baf-a29f-3f19a62bbf5d",
            "passphrase": "passphrase",
            "permission": "General",
            "ipWhitelist": "",
            "createdAt": 1661150688000
         }
        """
        params = {
            'subName': sub_name,
            'passphrase': passphrase,
            'remark': remark
        }
        if kwargs:
            params.update(kwargs)

        return self._request('POST', '/api/v1/sub/api-key', params=params)

    def modify_sub_account_apis(self, sub_name, api_key, passphrase, **kwargs):
        """
        https://docs.kucoin.com/futures/#modify-sub-account-futures-apis
        :param sub_name: Sub-account name
        :type: str
        :param passphrase: Password of API key
        :type: str
        :param api_key: API-Key(Sub-account APIKey)
        :type: str
        :param kwargs:  [Optional]  permission, ipWhitelist, expire
        :return:
         {
            "subName": "AAAAAAAAAA0007",
            "apiKey": "630329b4e7508700018298c5",
            "permission": "General",
            "ipWhitelist": "127.0.0.1",
         }
        """
        params = {
            'subName': sub_name,
            'passphrase': passphrase,
            'apiKey': api_key
        }
        if kwargs:
            params.update(kwargs)

        return self._request('POST', '/api/v1/sub/api-key/update', params=params)

    def delete_sub_account_apis(self, sub_name, api_key, passphrase):
        """
        https://docs.kucoin.com/futures/#delete-sub-account-futures-apis
        :param sub_name: Sub-account name(The sub-account name corresponding to the API key)
        :type: str
        :param passphrase: Password(Password of the API key)
        :type: str
        :param api_key: API-Key(API key to be deleted)
        :type: str
        :return:
         {
           "subName": "AAAAAAAAAA0007",
           "apiKey": "630325e0e750870001829864"
         }
        """
        params = {
            'subName': sub_name,
            'passphrase': passphrase,
            'apiKey': api_key
        }

        return self._request('DELETE', '/api/v1/sub/api-key', params=params)

    def get_account_overview_all(self, currency="XBT"):
        """
        https://www.kucoin.com/zh-hant/docs/rest/funding/funding-overview/get-all-sub-accounts-balance-futures
        :param currency: string Currecny ,including XBT,USDT,Default XBT
        :return:
          {
            "success": true,
            "code": "200",
            "msg": "success",
            "retry": false,
            "data": {
                "summary": {
                    "accountEquityTotal": 9.99,
                    "unrealisedPNLTotal": 0,
                    "marginBalanceTotal": 9.99,
                    "positionMarginTotal": 0,
                    "orderMarginTotal": 0,
                    "frozenFundsTotal": 0,
                    "availableBalanceTotal": 9.99,
                    "currency": "USDT"
                },
                "accounts": [
                    {
                        "accountName": "main",
                        "accountEquity": 9.99,
                        "unrealisedPNL": 0,
                        "marginBalance": 9.99,
                        "positionMargin": 0,
                        "orderMargin": 0,
                        "frozenFunds": 0,
                        "availableBalance": 9.99,
                        "currency": "USDT"
                    },
                    {
                        "accountName": "subacct",
                        "accountEquity": 0,
                        "unrealisedPNL": 0,
                        "marginBalance": 0,
                        "positionMargin": 0,
                        "orderMargin": 0,
                        "frozenFunds": 0,
                        "availableBalance": 0,
                        "currency": "USDT"
                    }
                ]
            }
        }
        """
        params = {
            'currency': currency
        }

        return self._request('GET', '/api/v1/account-overview-all', params=params)
