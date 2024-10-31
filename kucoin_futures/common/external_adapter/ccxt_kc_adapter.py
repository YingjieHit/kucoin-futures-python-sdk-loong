

# 合约转化
KC_TO_CCXT_CONTRACT = {
    'XBTUSDTM': 'BTC/USDT:USDT',
    'ETHUSDTM': 'ETH/USDT:USDT',
    'SOLUSDTM': 'SOL/USDT:USDT',
}


class CcxtKcAdapter(object):

    def __init__(self):
        pass

    @staticmethod
    def kc_symbol_to_ccxt(symbol: str) -> str:
        return KC_TO_CCXT_CONTRACT[symbol]


ccxt_kc_adapter = CcxtKcAdapter()
