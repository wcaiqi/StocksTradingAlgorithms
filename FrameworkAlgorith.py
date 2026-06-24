# region imports
from AlgorithmImports import *
# endregion
from datetime import timedelta
class MOMAlphaModel(AlphaModel): 
    def __init__(self):
        self.mom = []
    def on_securities_changed(self, algorithm, changes):
        for security in changes.added_securities:
            symbol = security.symbol
            self.mom.append({"symbol":symbol, "indicator":algorithm.MOM(symbol, 14, Resolution.DAILY)})
    def update(self, algorithm, data):
        ordered = sorted(self.mom, key=lambda kv: kv["indicator"].current.value, reverse=True)
        return Insight.group([Insight.price(ordered[0]['symbol'], timedelta(1), InsightDirection.UP), Insight.price(ordered[1]['symbol'], timedelta(1), InsightDirection.FLAT) ])
 
class FrameworkAlgorithm(QCAlgorithm):
    
    def initialize(self):
        self.set_start_date(2013, 10, 1)   
        self.set_end_date(2013, 12, 1)    
        self.set_cash(100000)           
        symbols = [Symbol.create(x, SecurityType.EQUITY, Market.USA) for x in ["SPY", "BND"]]
        self.universe_settings.resolution = Resolution.DAILY
        self.set_universe_selection(ManualUniverseSelectionModel(symbols))
        self.set_alpha(MOMAlphaModel())
        self.set_portfolio_construction(EqualWeightingPortfolioConstructionModel())
        self.set_risk_management(MaximumDrawdownPercentPerSecurity(0.02))
        
        #1. Set the Execution Model to an Immediate Execution Model
        self.set_execution(ImmediateExecutionModel())
    
