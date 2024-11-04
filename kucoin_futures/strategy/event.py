from kucoin_futures.strategy.object import (Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder, Bar,
                                            Level2Depth5)


class EventType:
    """事件类型"""
    TICKER = 'TICKER'
    LEVEL2DEPTH5 = 'LEVEL2DEPTH5'
    TRADE_ORDER = 'TRADE_ORDER'
    CREATE_MARKET_MAKER_ORDER = 'CREATE_MARKET_MAKER_ORDER'
    CREATE_ORDER = 'CREATE_ORDER'
    CANCEL_ALL_ORDER = 'CANCEL_ALL_ORDER'
    CANCEL_ORDER = 'CANCEL_ORDER'
    ACCOUNT_BALANCE = 'ACCOUNT_BALANCE'
    POSITION_CHANGE = 'POSITION_CHANGE'
    POSITION_SETTLEMENT = 'POSITION_SETTLEMENT'
    BAR = 'BAR'

    OKX_ORDER_BOOK5 = 'OKX_ORDER_BOOK5'


class Event(object):
    def __init__(self, data):
        self.type: str = ''
        self.data = data


class TickerEvent(Event):
    """市场ticker数据事件"""

    def __init__(self, data: Ticker):
        super().__init__(data)
        self.type = EventType.TICKER


class Level2Depth5Event(Event):
    """市场Level2Depth5数据事件"""

    def __init__(self, data: Level2Depth5):
        super().__init__(data)
        self.type = EventType.LEVEL2DEPTH5


class BarEvent(Event):
    """市场bar数据事件"""

    def __init__(self, data: Bar):
        super().__init__(data)
        self.type = EventType.BAR


class TraderOrderEvent(Event):
    """订单回报事件"""

    def __init__(self, data: Order):
        super().__init__(data)
        self.type = EventType.TRADE_ORDER


class CreateMarketMakerOrderEvent(Event):
    """发送market maker order事件"""

    def __init__(self, data: MarketMakerCreateOrder):
        super().__init__(data)
        self.type = EventType.CREATE_MARKET_MAKER_ORDER


class CreateOrderEvent(Event):
    """发送order事件"""

    def __init__(self, data: CreateOrder):
        super().__init__(data)
        self.type = EventType.CREATE_ORDER


class CancelAllOrderEvent(Event):
    """撤销所有order事件"""

    def __init__(self, data: str):
        super().__init__(data)
        self.type = EventType.CANCEL_ALL_ORDER


class CancelOrderEvent(Event):
    """撤销order事件"""

    def __init__(self, data: CancelOrder):
        super().__init__(data)
        self.type = EventType.CANCEL_ORDER


class AccountBalanceEvent(Event):
    """账户余额更变"""

    def __init__(self, data: dict):
        super().__init__(data)
        self.type = EventType.ACCOUNT_BALANCE

class PositionChangeEvent(Event):
    """持仓变化事件"""
    def __init__(self, data: dict):
        super().__init__(data)
        self.type = EventType.POSITION_CHANGE

class PositionSettlementEvent(Event):
    """持仓结算事件"""
    def __init__(self, data: dict):
        super().__init__(data)
        self.type = EventType.POSITION_SETTLEMENT

class OkxOrderBook5Event(Event):
    """okx order book5事件"""
    def __init__(self, data: dict):
        super().__init__(data)
        self.type = EventType.OKX_ORDER_BOOK5
