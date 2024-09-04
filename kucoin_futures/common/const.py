


# 定义合约的最小跳价单位
PRICE_INTERVAL = {
    'XBTUSDTM': 0.1,
    'ETHUSDTM': 0.01,
    'TRBUSDTM': 0.01,
    'OPUSDTM': 0.0001,
    'SOLUSDTM': 0.001,
    'JASMYUSDTM': 0.000001,
    'PEPEUSDTM': 0.0000000001,
    'FLOKIUSDTM': 0.000000001,
    'NOTUSDTM': 0.000001,
    'DOGEUSDTM': 0.00001,
    'INJUSDTM': 0.001,
    'WIFUSDTM': 0.0001,
    # 'XRPUSDTM': 0.0001,  # 应该是0.0001，但是ASQ模型无法拟合？
    'ORDIUSDTM': 0.0001,
    'SHIBUSDTM': 0.000000001,
    'FETUSDTM': 0.0001,
    'TONUSDTM': 0.0001,
    'ADAUSDTM': 0.00001,
    'BNBUSDTM': 0.01,
    'LINKUSDTM': 0.001,
    'KASUSDTM': 0.000001,
    'ONDOUSDTM': 0.0001,
    'FTMUSDTM': 0.0001,

    'BTC-USDT': 0.1,
    'ETH-USDT': 0.01,
    'SOL-USDT': 0.001,
}


# 定义合约的最小数量
MIN_SIZE = {
    'BTC-USDT': 0.00001,
    'ETH-USDT': 0.0001,
    'SOL-USDT': 0.01,
}

# 定义kc和bn之间的合约转化,指的是订阅到的合约
BN_TO_KC_SYMBOL = {
    'BTCUSD_PERP': 'XBTUSDM',
    'ETHUSD_PERP': 'ETHUSDM',

}

# 定义kc和bn之间的合约转化,指的是订阅到的合约
KC_TO_BN_SYMBOL = {
    'XBTUSDM': 'BTCUSD_PERP',
    'ETHUSDM': 'ETHUSD_PERP',
}

# 定义kc和bn之间的周期转化
KC_TO_BN_FREQUENCY = {
    '1min': '1m',
    '5min': '5m',
    '15min': '15m',
    '30min': '30m',
    '1hour': '1h',
    '4hour': '4h',
    '1day': '1d',
}
