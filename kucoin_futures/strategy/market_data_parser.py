from kucoin_futures.strategy.object import (Ticker, Order, AccountBalance, Bar, Level2Depth5)


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
            ts=msg.get('ts')
        )


market_data_parser = MarketDataParser()
