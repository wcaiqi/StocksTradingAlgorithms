# region imports
from AlgorithmImports import *
# endregion
class SMAPairsTrading(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2018, 7, 1)   
        self.set_end_date(2025, 3, 31)
        self.set_cash(100000)
        
        symbols = [Symbol.create(x, SecurityType.EQUITY, Market.USA) for x in ["PEP", "KO"]]
        self.add_universe_selection(ManualUniverseSelectionModel(symbols))
        self.universe_settings.resolution = Resolution.HOUR
        self.universe_settings.data_normalization_mode = DataNormalizationMode.RAW
        self.add_alpha(PairsTradingAlphaModel())
        self.set_portfolio_construction(EqualWeightingPortfolioConstructionModel())
        self.set_execution(ImmediateExecutionModel())
        
    def on_end_of_day(self, symbol):
        self.log("Taking a position of " + str(self.portfolio[symbol].quantity) + " units of symbol " + str(symbol))

class PairsTradingAlphaModel(AlphaModel):

    def __init__(self):
        self.pair = [ ]
        self.spread_mean = SimpleMovingAverage(500)
        self.spread_std = StandardDeviation(500)
        self.period = timedelta(hours=2)
        
    def update(self, algorithm, data):
        spread = self.pair[1].price - self.pair[0].price
        self.spread_mean.update(algorithm.time, spread)
        self.spread_std.update(algorithm.time, spread) 
        
        upperthreshold = self.spread_mean.current.value + self.spread_std.current.value
        lowerthreshold = self.spread_mean.current.value - self.spread_std.current.value

        if spread > upperthreshold:
            return Insight.group(
                [
                    Insight.price(self.pair[0].symbol, self.period, InsightDirection.UP),
                    Insight.price(self.pair[1].symbol, self.period, InsightDirection.DOWN)
                ])
        
        if spread < lowerthreshold:
            return Insight.group(
                [
                    Insight.price(self.pair[0].symbol, self.period, InsightDirection.DOWN),
                    Insight.price(self.pair[1].symbol, self.period, InsightDirection.UP)
                ])

        return []
    
    def on_securities_changed(self, algorithm, changes):
        self.pair = [x for x in changes.added_securities]
        
        #1. Call for 500 bars of history data for each symbol in the pair and save to the variable history
        history = algorithm.history([x.symbol for x in self.pair], 500)
        #2. Unstack the Pandas data frame to reduce it to the history close price
        history = history.close.unstack(level=0)
        #3. Iterate through the history tuple and update the mean and standard deviation with historical data 
        for tuple in history.itertuples():
            self.spread_mean.update(tuple[0], tuple[2]-tuple[1])
            self.spread_std.update(tuple[0], tuple[2]-tuple[1])
