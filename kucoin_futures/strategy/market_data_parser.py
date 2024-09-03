from kucoin_futures.strategy.object import (Ticker, Order, AccountBalance, Bar, Level2Depth5)
from kucoin_futures.common.const import BN_TO_KC_SYMBOL


class MarketDataParser(object):

    @staticmethod
    def parse_level2_depth5(msg: dict) -> Level2Depth5:
        """
        解析Level2Depth5数据
        """
        topic = msg.get('topic')
        symbol = topic.split(':')[1]
        data = msg.get('data')
        ask_prices = []
        ask_sizes = []
        bid_prices = []
        bid_sizes = []
        for ask in data.get('asks'):
            ask_prices.append(float(ask[0]))
            ask_sizes.append(ask[1])
        for bid in data.get('bids'):
            bid_prices.append(float(bid[0]))
            bid_sizes.append(bid[1])

        return Level2Depth5(
            symbol=symbol,
            ask_prices=ask_prices,
            ask_sizes=ask_sizes,
            bid_prices=bid_prices,
            bid_sizes=bid_sizes,
            ts=data.get('ts')
        )

    @staticmethod
    def parse_bar(msg: dict) -> Bar:
        """
        解析Bar数据
        """
        data = msg.get('data')
        candles = data.get('candles')
        return Bar(
            symbol=data.get('symbol'),
            ts= int(candles[0]),
            open=float(candles[1]),
            close=float(candles[2]),
            high=float(candles[3]),
            low=float(candles[4]),
            turnover=float(candles[5]),  # 官方不推荐使用该字段
            volume=int(candles[6]),
        )

    @staticmethod
    def parse_bn_bar(msg: dict) -> Bar:
        """
        解析bn Bar数据
        """
        k = msg.get('k')
        return Bar(
            symbol=BN_TO_KC_SYMBOL.get(msg.get('s')),
            ts=k.get('t')//1e3,
            open=float(k.get('o')),
            close=float(k.get('c')),
            high=float(k.get('h')),
            low=float(k.get('l')),
            turnover=float(k.get('q')),  # 官方不推荐使用该字段
            volume=int(k.get('v')),
        )

    @staticmethod
    def parse_order(msg: dict) -> Order:
        """
        解析Order数据
        """
        order_data = msg.get('data')
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


market_data_parser = MarketDataParser()
