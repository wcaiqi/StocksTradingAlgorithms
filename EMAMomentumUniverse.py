# region imports
from AlgorithmImports import *
# endregion
class EMAMomentumUniverse(QCAlgorithm):

    def Initialize(self):
        self.set_start_date(2019, 1, 7)
        self.set_end_date(2019, 4, 1)
        self.set_cash(100000)
        self.universe_settings.resolution = Resolution.DAILY
        self.add_universe(self.select)
        self.averages = { }

    def select(self, fundamental):
        selected = []
        fundamental = sorted([x for x in fundamental if x.price > 10],
            key=lambda x: x.dollar_volume, reverse=True)[:100]

        for stock in fundamental:
            symbol = stock.symbol

            if symbol not in self.averages:
                # 1. Call history to get an array of 200 days of history data
                history = self.history[TradeBar](symbol, 200, Resolution.DAILY)

                #2. Adjust SelectionData to pass in the history result
                self.averages[symbol] = SelectionData(history)

            self.averages[symbol].update(self.time, stock.adjusted_price)

            if  self.averages[symbol].is_ready() and self.averages[symbol].fast > self.averages[symbol].slow:
                selected.append(symbol)

        return selected[:10]

    def on_securities_changed(self, changes):
        for security in changes.removed_securities:
            self.liquidate(security.symbol)

        for security in changes.added_securities:
            self.set_holdings(security.symbol, 0.10)

class SelectionData():
    #3. Update the constructor to accept a history array
    def __init__(self, history):
        self.slow = ExponentialMovingAverage(200)
        self.fast = ExponentialMovingAverage(50)

        #4. Loop over the history data and update the indicators
        for bar in history:
            self.update(bar.end_time, bar.close)

    def is_ready(self):
        return self.slow.is_ready and self.fast.is_ready

    def update(self, time, price):
        self.fast.update(time, price)
        self.slow.update(time, price)
