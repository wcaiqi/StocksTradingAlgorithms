# region imports
from AlgorithmImports import *
# endregion
class SectorBalancedPortfolioConstruction(QCAlgorithm):
    def Initialize(self):
        self.set_start_date(2016, 12, 28) 
        self.set_end_date(2017, 3, 1) 
        self.set_cash(100000) 
        self.universe_settings.resolution = Resolution.HOUR
        self.set_universe_selection(MyUniverseSelectionModel())
        self.set_alpha(ConstantAlphaModel(InsightType.PRICE, InsightDirection.UP, timedelta(1), 0.025, None))
        self.set_portfolio_construction(MySectorWeightingPortfolioConstructionModel(Resolution.DAILY))
        self.set_execution(ImmediateExecutionModel())

class MyUniverseSelectionModel(FundamentalUniverseSelectionModel):
    def select(self, algorithm, fundamental):
        fundamental = sorted([x for x in fundamental if x.market_cap > 0],
            key=lambda x: x.dollar_volume, reverse=True)[:100]
        filtered = [f for f in fundamental if f.asset_classification.morningstar_sector_code == MorningstarSectorCode.TECHNOLOGY]
        technology = sorted(filtered, key=lambda f: f.market_cap, reverse=True)[:3]
        filtered = [f for f in fundamental if f.asset_classification.morningstar_sector_code == MorningstarSectorCode.FINANCIAL_SERVICES]
        financial_services = sorted(filtered, key=lambda f: f.market_cap, reverse=True)[:2]
        filtered = [f for f in fundamental if f.asset_classification.morningstar_sector_code == MorningstarSectorCode.CONSUMER_DEFENSIVE]
        consumer_defensive = sorted(filtered, key=lambda f: f.market_cap, reverse=True)[:1]
        return [x.symbol for x in technology + financial_services + consumer_defensive]
        
class MySectorWeightingPortfolioConstructionModel(EqualWeightingPortfolioConstructionModel):
    def __init__(self, rebalance = Resolution.DAILY):
        super().__init__(rebalance)
        self.symbol_by_sector_code = dict()
        self.result = dict()

    def determine_target_percent(self, activeInsights):
        #1. Set the self.sector_buying_power before by dividing one by the length of self.symbol_by_sector_code
        self.sector_buying_power = 1/len(self.symbol_by_sector_code)

        for sector, symbols in self.symbol_by_sector_code.items():
            #2. Search for the active insights in this sector. Save the variable self.insights_in_sector
            self.insights_in_sector = [insight for insight in activeInsights if insight.symbol in symbols]

            #3. Divide the self.sector_buying_power by the length of self.insights_in_sector to calculate the variable percent
            # The percent is the weight we'll assign the direction of the insight
            self.percent = self.sector_buying_power / len(self.insights_in_sector)

            #4. For each insight in self.insights_in_sector, assign each insight an allocation. 
            # The allocation is calculated by multiplying the insight direction by the self.percent 
            for insight in self.insights_in_sector:
                self.result[insight] = insight.Direction * self.percent

        return self.result


    def on_securities_changed(self, algorithm, changes):
        for security in changes.added_securities:
            sector_code = security.fundamentals.asset_classification.morningstar_sector_code
            if sector_code not in self.symbol_by_sector_code:
                self.symbol_by_sector_code[sector_code] = list()
            self.symbol_by_sector_code[sector_code].append(security.symbol) 

        for security in changes.removed_securities:
            sector_code = security.fundamentals.asset_classification.morningstar_sector_code
            if sector_code in self.symbol_by_sector_code:
                symbol = security.symbol
                if symbol in self.symbol_by_sector_code[sector_code]:
                    self.symbol_by_sector_code[sector_code].remove(symbol)

        super().on_securities_changed(algorithm, changes)

