

# 合约转化
KC_TO_CCXT_CONTRACT = {
    'XBTUSDTM': 'BTC/USDT:USDT',
    'ETHUSDTM': 'ETH/USDT:USDT',
    'SOLUSDTM': 'SOL/USDT:USDT',
}

CCXT_TO_KC_CONTRACT = {
    'BTC/USDT:USDT': 'XBTUSDTM',
    'ETH/USDT:USDT': 'ETHUSDTM',
    'SOL/USDT:USDT': 'SOLUSDTM',
}

class CcxtKcAdapter(object):

    def __init__(self):
        pass

    @staticmethod
    def kc_symbol_to_ccxt(symbol: str) -> str:
        return KC_TO_CCXT_CONTRACT[symbol]

    @staticmethod
    def ccxt_symbol_to_kc(symbol: str) -> str:
        return CCXT_TO_KC_CONTRACT[symbol]

ccxt_kc_adapter = CcxtKcAdapter()
