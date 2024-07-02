
from kucoin_futures.strategy.object import Ticker, Order, MarketMakerCreateOrder, CreateOrder, CancelOrder


class EventType:
    """事件类型"""
    TICKER = 'TICKER'
    TRADE_ORDER = 'TRADE_ORDER'
    CREATE_MARKET_MAKER_ORDER = 'CREATE_MARKET_MAKER_ORDER'
    CREATE_ORDER = 'CREATE_ORDER'
    CANCEL_ALL_ORDER = 'CANCEL_ALL_ORDER'
    CANCEL_ORDER = 'CANCEL_ORDER'
    ACCOUNT_BALANCE = 'ACCOUNT_BALANCE'


class Event(object):
    def __init__(self, data):
        self.type: str = ''
        self.data = data


class TickerEvent(Event):
    """市场ticker数据事件"""

    def __init__(self, data: Ticker):
        super().__init__(data)
        self.type = EventType.TICKER


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