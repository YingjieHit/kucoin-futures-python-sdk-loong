
from dataclasses import dataclass


@dataclass
class Ticker:
    """ticker数据字段"""
    symbol: str
    sequence: int
    bid_size: float
    bid_price: float  # 数据源为str需转化
    ask_price: float  # 数据源为str需转化
    ask_size: float
    ts: int

@dataclass
class Order:
    """订单(返回)字段"""
    symbol: str  # "symbol": "XBTUSDM", // 合約symbol
    side: str  # "side": "buy", // 訂單方向，買或賣
    order_id: str  # "orderId": "5cdfc138b21023a909e5ad55", // 訂單號
    type: str  # "type": "match", // 消息類型，取值列表: "open", "match", "filled", "canceled", "update"
    fee_type: str  # "feeType": "takerFee", // 費用類型，當type = match才包含此字段，取值列表: "takerFee", "makerFee"
    status: str  # "status": "open", // 訂單狀態: "match", "open", "done"
    match_size: float  # "matchSize": "", //成交數量 (當類型爲"match"時包含此字段)
    match_price: float  # "matchPrice": "",//成交價格 (當類型爲"match"時包含此字段)
    order_type: str  # "orderType": "limit", //訂單類型, "market"表示市價單", "limit"表示限價單
    price: float  # "price": "3600",  //訂單價格
    size: float  # "size": "20000",  //訂單數量
    remain_size: float  # "remainSize": "20001",  //訂單剩餘可用於交易的數量
    fill_size: float  # "filledSize":"20000",  //訂單已成交的數量
    canceled_size: float  # "canceledSize": "0",  //  update消息中，訂單減少的數量
    trade_id: str  # "tradeId": "5ce24c16b210233c36eexxxx",  //交易號(當類型爲"match"時包含此字段)
    client_oid: str  # "clientOid": "5ce24c16b210233c36ee321d", //用戶自定義ID
    order_time: int  # "orderTime": 1545914149935808589,  // 下單時間(trade模塊生成)
    old_size: float  # "oldSize ": "15000", // 更新前的數量(當類型爲"update"時包含此字段)
    liquidity: str  # "liquidity": "maker", // 成交方向，取taker一方的買賣方向
    ts: int  # "ts": 1545914149935808589 // 時間戳（撮合時間）


@dataclass
class MarketMakerCreateOrder:
    """market maker order字段"""
    symbol: str
    lever: float
    size: float
    price_buy: float
    price_sell: float
    client_oid_buy: str
    client_oid_sell: str
    post_only: bool


@dataclass
class CreateOrder:
    """ 创建订单字段 """
    symbol: str
    lever: float
    size: float
    side: str
    price: float
    type: str
    client_oid: str = ''
    post_only: bool = True


@dataclass
class CancelOrder:
    """撤单字段"""
    symbol: str = ''
    client_oid: str = ''
    order_id: str = ''
