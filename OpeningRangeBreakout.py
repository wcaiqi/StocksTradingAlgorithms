# region imports
from AlgorithmImports import *
# endregion

class OpeningRangeBreakout(QCAlgorithm):
    
    opening_bar = None 
    
    def initialize(self):
        self.set_start_date(2018, 7, 10)  
        self.set_end_date(2019, 6, 30)  
        self.set_cash(100000)
        self.add_equity("TSLA", Resolution.MINUTE)
        self.consolidate("TSLA", timedelta(minutes=30), self.on_data_consolidated)
        
        #3. Create a scheduled event triggered at 13:30 calling the close_positions function
        self.schedule.on(self.date_rules.every_day("TSLA"), self.time_rules.at(13,30), self.close_positions)
    def on_data(self, data):
        
        if self.portfolio.invested or self.opening_bar is None:
            return
        
        if data["TSLA"].close > self.opening_bar.high:
            self.set_holdings("TSLA", 1)

        elif data["TSLA"].close < self.opening_bar.low:
            self.set_holdings("TSLA", -1)  
         
    def on_data_consolidated(self, bar):
        if bar.time.hour == 9 and bar.time.minute == 30:
            self.opening_bar = bar
    
    #1. Create a function named close_positions(self)
        #2. Set self.opening_bar to None, and liquidate TSLA 
    def close_positions(self):
        self.opening_bar = None
        self.liquidate("TSLA")
