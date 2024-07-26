from uuid import uuid1
from decimal import Decimal, getcontext, ROUND_HALF_UP
from kucoin_futures.strategy.object import Ticker, Order, AccountBalance, Bar


class Utils(object):

    @staticmethod
    def spot_dict_2_account_balance(balance_data) -> AccountBalance:
        """
        将spot的balance数据的字典转换为AccountBalance对象，使用字典的get方法来避免KeyError。
        """
        return AccountBalance(
            account_id=balance_data.get("accountId"),
            available=float(balance_data.get("available")),
            available_change=float(balance_data.get("availableChange")),
            currency=balance_data.get("currency"),
            hold=float(balance_data.get("hold")),
            hold_change=float(balance_data.get("holdChange")),
            relation_context=balance_data.get("relationContext"),
            relation_event=balance_data.get("relationEvent"),
            relation_event_id=balance_data.get("relationEventId"),
            ts=int(balance_data.get("time")),
            total=float(balance_data.get("total"))
        )

    # TODO: 该方法为现货相关，只是暂时写在这里，后期需考虑合理的现货与合约结合的架构
    @staticmethod
    def spot_level2_2_ticker(level2_data) -> Ticker:
        """
        将spot的level2数据的字典转换为Ticker对象，使用字典的get方法来避免KeyError。
        """
        return Ticker(
            symbol=level2_data.get("symbol"),
            sequence=level2_data.get("sequence", 0),  # 提供默认值为0
            bid_size=float(level2_data["bids"][0][1]),  # 需要转换为float
            bid_price=float(level2_data['bids'][0][0]),  # 转换为float
            ask_price=float(level2_data['asks'][0][0]),  # 转换为float
            ask_size=float(level2_data['asks'][0][1]),  # 默认值0，转换为float
            ts=level2_data.get("timestamp", 0)  #
        )

    @staticmethod
    def spot_candle_2_bar(candle_data: dict) -> Bar:
        """
        将spot的candle数据的字典转换为Bar对象，使用字典的get方法来避免KeyError。
        """
        candles = candle_data.get("candles")
        return Bar(
            symbol=candle_data.get("symbol"),
            ts=int(candles[0]),
            open=float(candles[1]),
            close=float(candles[2]),
            high=float(candles[3]),
            low=float(candles[4]),
            volume=float(candles[5]),
            turnover=float(candles[6]),
        )

    @staticmethod
    def spot_candles_2_bars(symbol: str, candles_data: list) -> list:
        """
        将spot的candles数据的数组(由rest接口读取)转换为Bar对象，使用字典的get方法来避免KeyError。
        """
        bars = []
        for candle in candles_data:
            bar = Bar(
                symbol=symbol,
                ts=int(candle[0]),
                open=float(candle[1]),
                close=float(candle[2]),
                high=float(candle[3]),
                low=float(candle[4]),
                volume=float(candle[5]),
                turnover=float(candle[6]),
            )
            bars.append(bar)
        # 如果发现ts是从大到小排列，则倒序
        if bars[0].ts > bars[-1].ts:
            bars.reverse()
        return bars

    # TODO: 该方法为现货相关，只是暂时写在这里，后期需考虑合理的现货与合约结合的架构
    @staticmethod
    def spot_dict_2_ticker(ticker_data: dict) -> Ticker:
        """
        将spot的ticker数据的字典转换为Ticker对象，使用字典的get方法来避免KeyError。
        """
        return Ticker(
            symbol=ticker_data.get("symbol"),
            sequence=ticker_data.get("sequence", 0),  # 提供默认值为0
            bid_size=float(ticker_data.get("bestBidSize", 0)),  # 默认值0，需要转换为float
            bid_price=float(ticker_data.get("bestBid", 0)),  # 默认值0，转换为float
            ask_price=float(ticker_data.get("bestAsk", 0)),  # 默认值0，转换为float
            ask_size=float(ticker_data.get("bestAskSize", 0)),  # 默认值0，转换为float
            ts=ticker_data.get("time", 0)  # 提供默认值为0
        )

    # TODO: 该方法为现货相关，只是暂时写在这里，后期需考虑合理的现货与合约结合的架构
    @staticmethod
    def spot_dict_2_order(order_data: dict) -> Order:
        """
        将spot的order数据的字典转换为Order对象，使用字典的get方法来避免KeyError。
        """
        order = Order(
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
            canceled_size=float(order_data.get('canceledSize', 0)),  # "canceledSize": "0", update消息中，訂單減少的數量  注意：现货无该字段
            trade_id=order_data.get('tradeId', ''),  # "tradeId": "5ce24c16b210233c36eexxxx", 交易號(當類型爲"match"時包含此字段)
            client_oid=order_data.get('clientOid', ''),  # "clientOid": "5ce24c16b210233c36ee321d", //用戶自定義ID
            order_time=order_data.get('orderTime', 0),  # "orderTime": 1545914149935808589,  // 下單時間(trade模塊生成)
            old_size=float(order_data.get('oldSize', 0)),  # "oldSize ": "15000", // 更新前的數量(當類型爲"update"時包含此字段)
            liquidity=order_data.get('liquidity', ''),  # "liquidity": "maker" "taker"
            ts=order_data.get('ts', 0)  # "ts": 1545914149935808589 // 時間戳（撮合時間）单位是ns
        )
        order.fill_size = order.size - order.remain_size
        return order

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

    @staticmethod
    def round_decimal(value, n):
        """
        Rounds a float to at most n decimal places.

        Args:
        value (float): The number to be rounded.
        n (int): The maximum number of decimal places to keep.

        Returns:
        Decimal: The rounded number as a Decimal, to maintain precision.
        """
        # 设置 Decimal 的精度和四舍五入模式
        getcontext().prec = 28  # 设置足够的精度以处理常见情况
        getcontext().rounding = ROUND_HALF_UP

        # 使用 Decimal 进行计算
        decimal_value = Decimal(value)
        rounded_value = decimal_value.quantize(Decimal('1.' + '0' * n), rounding=ROUND_HALF_UP)

        return rounded_value

    @staticmethod
    def calc_decimal_places(number):
        """
        获取一个数字的小数点后面位数
        """
        # 将数字转换为字符串
        str_num = str(number)
        # 检查是否包含小数点
        if '.' in str_num:
            # 分割字符串，取小数点后的部分，并计算其长度
            decimal_part = str_num.split('.')[1]
            return len(decimal_part)
        else:
            # 如果没有小数点，则返回0
            return 0

    @staticmethod
    def insure_decimals(number, decimal_places):
        """
        保留小数位数
        """
        # 将数字转换为字符串
        str_num = str(number)
        # 检查是否包含小数点
        if '.' in str_num:
            # 分割字符串，取小数点后的部分，并计算其长度
            decimal_part = str_num.split('.')[1]
            # 如果小数部分的长度大于需要保留的位数，则截取
            if len(decimal_part) > decimal_places:
                return float(str_num[:str_num.index('.') + decimal_places + 1])
            else:
                return number
        else:
            # 如果没有小数点，则返回0
            return number

    @staticmethod
    def create_client_oid():
        return ''.join([each for each in str(uuid1()).split('-')])


utils = Utils()
