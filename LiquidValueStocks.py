# region imports
from AlgorithmImports import *
# endregion
class LiquidValueStocks(QCAlgorithm):

    def Initialize(self):
        self.set_start_date(2017, 5, 15)
        self.set_end_date(2017, 7, 15)
        self.set_cash(100000)
        self.universe_settings.resolution = Resolution.HOUR
        self.add_universe_selection(LiquidValueUniverseSelectionModel())
        
        #1. Create and instance of the LongShortEYAlphaModel
        self.set_alpha(LongShortEYAlphaModel())
        self.set_portfolio_construction(EqualWeightingPortfolioConstructionModel())
        self.set_execution(ImmediateExecutionModel())

class LiquidValueUniverseSelectionModel(FundamentalUniverseSelectionModel):
    last_month = -1

    def select(self, algorithm, fundamental):
        if self.last_month == algorithm.time.month:
            return Universe.UNCHANGED
        self.last_month = algorithm.time.month

        sorted_by_dollar_volume = sorted([x for x in fundamental if x.has_fundamental_data],
            key=lambda x: x.dollar_volume, reverse=True)

        fundamental = sorted_by_dollar_volume[:100]

        sorted_by_yields = sorted(fundamental, key=lambda f: f.valuation_ratios.earning_yield, reverse=True)
        universe = sorted_by_yields[:10] + sorted_by_yields[-10:]
        return [f.symbol for f in universe]

# Define the LongShortAlphaModel class  
class LongShortEYAlphaModel(AlphaModel):
    last_month = -1

    def update(self, algorithm, data):
        insights = []
        
        #2. If else statement to emit signals once a month 
        if self.last_month == algorithm.time.month:
            return insights
        else:
            self.last_month = algorithm.time.month

        #3. For loop to emit insights with insight directions 
        # based on whether earnings yield is greater or less than zero once a month
        for symbol, security in algorithm.active_securities.items():
            if security.fundamentals.valuation_ratios.earning_yield > 0:
                direction = InsightDirection.UP 
            else:
                direction = InsightDirection.DOWN
            
        insights.append(Insight.price(symbol, timedelta(28), direction))
        return insights

