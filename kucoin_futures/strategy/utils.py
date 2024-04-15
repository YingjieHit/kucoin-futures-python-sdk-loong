
from kucoin_futures.strategy.object import Ticker, Order


class Utils(object):

    @staticmethod
    def dict_2_ticker(ticker_data: dict) -> Ticker:
        """
        将ticker数据的字典转换为Ticker对象，使用字典的get方法来避免KeyError。
        """
        return Ticker(
            symbol=ticker_data.get("symbol"),
            sequence=ticker_data.get("sequence", 0),  # 提供默认值为0
            bid_size=ticker_data.get("bestBidSize", 0),  # 默认值0，需要转换为float
            bid_price=float(ticker_data.get("bestBidPrice", 0)),  # 默认值0，转换为float
            ask_price=float(ticker_data.get("bestAskPrice", 0)),  # 默认值0，转换为float
            ask_size=ticker_data.get("bestAskSize", 0),  # 默认值0，转换为float
            ts=ticker_data.get("ts", 0)  # 提供默认值为0
        )

    @staticmethod
    def dict_2_order(order_data: dict) -> Order:
        """
        将order数据的字典转换为Order对象，使用字典的get方法来避免KeyError。
        """
        return Order(
            symbol=order_data.get('symbol', ''),  # "symbol": "XBTUSDM"
            side=order_data.get('side', ''),  # 訂單方向，買或賣 "buy"  "sell"
            order_id=order_data.get('orderId', ''),  # "orderId": "5cdfc138b21023a909e5ad55", 訂單號
            type=order_data.get('type', ''),  # " 消息類型 "open", "match", "filled", "canceled", "update"
            fee_type=order_data.get('feeType', ''),  # 費用類型，當type = match才包含此字段，取值列表: "takerFee", "makerFee"
            status=order_data.get('status', ''),  # 訂單狀態: "match", "open", "done"
            match_size=float(order_data.get('matchSize', 0)),  # "matchSize": 成交數量 (當類型爲"match"時包含此字段)
            match_price=float(order_data.get('matchPrice', 0)),  # 成交價格 (當類型爲"match"時包含此字段)
            order_type=order_data.get('orderType', ''),  # 訂單類型, "market"表示市價單", "limit"表示限價單
            price=float(order_data.get('price', 0)),  # "price": "3600",  //訂單價格
            size=float(order_data.get('size', 0)),  # "size": "20000",  //訂單數量
            remain_size=float(order_data.get('remainSize', 0)),  # "remainSize": "20001",  //訂單剩餘可用於交易的數量
            fill_size=float(order_data.get('filledSize', 0)),  # "filledSize":"20000",  //訂單已成交的數量
            canceled_size=float(order_data.get('canceledSize', 0)),  # "canceledSize": "0", update消息中，訂單減少的數量
            trade_id=order_data.get('tradeId', ''),  # "tradeId": "5ce24c16b210233c36eexxxx", 交易號(當類型爲"match"時包含此字段)
            client_oid=order_data.get('clientOid', ''),  # "clientOid": "5ce24c16b210233c36ee321d", //用戶自定義ID
            order_time=order_data.get('orderTime', 0),  # "orderTime": 1545914149935808589,  // 下單時間(trade模塊生成)
            old_size=float(order_data.get('oldSize', 0)),  # "oldSize ": "15000", // 更新前的數量(當類型爲"update"時包含此字段)
            liquidity=order_data.get('liquidity', ''),  # "liquidity": "maker", // 成交方向，取taker一方的買賣方向
            ts=order_data.get('ts', 0)  # "ts": 1545914149935808589 // 時間戳（撮合時間）
        )


utils = Utils()
