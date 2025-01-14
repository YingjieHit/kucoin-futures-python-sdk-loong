

# 合约转化
KC_TO_CCXT_CONTRACT = {
    # U本位
    'XBTUSDTM': 'BTC/USDT:USDT',
    'ETHUSDTM': 'ETH/USDT:USDT',
    'SOLUSDTM': 'SOL/USDT:USDT',
    'XRPUSDTM': 'XRP/USDT:USDT',
    # 币本位
    'XBTUSDM': 'BTC/USD:BTC',
    'ETHUSDM': 'ETH/USD:ETH',
    'SOLUSDM': 'SOL/USD:SOL',
    'XRPUSDM': 'XRP/USD:XRP',
}

CCXT_TO_KC_CONTRACT = {
    # U本位
    'BTC/USDT:USDT': 'XBTUSDTM',
    'ETH/USDT:USDT': 'ETHUSDTM',
    'SOL/USDT:USDT': 'SOLUSDTM',
    'XRP/USDT:USDT': 'XRPUSDTM',
    # 币本位
    'BTC/USD:BTC': 'XBTUSDM',
    'ETH/USD:ETH': 'ETHUSDM',
    'SOL/USD:SOL': 'SOLUSDM',
    'XRP/USD:XRP': 'XRPUSDM',
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
