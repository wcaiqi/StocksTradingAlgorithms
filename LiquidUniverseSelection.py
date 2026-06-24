# region imports
from AlgorithmImports import *
# endregion
class LiquidUniverseSelection(QCAlgorithm):
    
    filtered_by_price = None
    
    def initialize(self):
        self.set_start_date(2019, 1, 11)
        self.set_end_date(2019, 7, 1)
        self.set_cash(100000)
        self.settings.daily_precise_end_time = False
        self.add_universe(self.select)
        self.universe_settings.resolution = Resolution.DAILY

        #1. Set the leverage to 2
        self.universe_settings.leverage =2

    def select(self, fundamental):
        filtered_by_price = [x for x in fundamental if x.price > 10]
        sorted_by_dollar_volume = sorted(filtered_by_price, key=lambda x: x.dollar_volume, reverse=True) 
        return [x.symbol for x in sorted_by_dollar_volume[:8]]

    def on_securities_changed(self, changes):
        self.changes = changes
        self.log(f"on_securities_changed({self.time}):: {changes}")
        
        for security in self.changes.removed_securities:
            if security.invested:
                self.liquidate(security.symbol)
        
        for security in self.changes.added_securities:
            #2. Leave a cash buffer by setting the allocation to 0.18 instead of 0.2 
            self.set_holdings(security.symbol, 0.2)
        
