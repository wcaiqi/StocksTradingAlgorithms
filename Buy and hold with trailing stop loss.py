# region imports
from AlgorithmImports import *
# endregion

class BootCampTask(QCAlgorithm):
    
    # Order ticket for our stop order, Datetime when stop order was last hit
    stop_market_ticket = None
    stop_market_order_fill_time = datetime.min
    highest_spy_price = -1
    
    def initialize(self):
        self.set_start_date(2018, 12, 1)
        self.set_end_date(2019, 4, 1)
        self.set_cash(100000)
        spy = self.add_equity("SPY", Resolution.DAILY, data_normalization_mode=DataNormalizationMode.RAW)
        
    def on_data(self, data):
        
        # 1. Plot the current SPY price to "Data Chart" on series "Asset Price"
        self.plot("Levels", "Asset Price", self.securities["SPY"].price)

        if (self.time - self.stop_market_order_fill_time).days < 15:
            return

        if not self.portfolio.invested:
            self.market_order("SPY", 500)
            self.stop_market_ticket = self.stop_market_order("SPY", -500, 0.9 * self.securities["SPY"].close)
            # The initial highest price is the current price
            self.highest_spy_price = self.securities["SPY"].close

        elif self.securities["SPY"].close > self.highest_spy_price:            
            self.highest_spy_price = self.securities["SPY"].close
            update_fields = UpdateOrderFields()
            update_fields.stop_price = self.highest_spy_price * 0.9
            self.stop_market_ticket.update(update_fields)
        #2. Plot the moving stop price on "Data Chart" with "Stop Price" series name
            self.plot("Levels", "Stop Price", self.securities["SPY"].price)
    def on_order_event(self, order_event):
        
        if order_event.status != OrderStatus.FILLED:
            return
        
        if self.stop_market_ticket is not None and self.stop_market_ticket.order_id == order_event.order_id: 
            self.stop_market_order_fill_time = self.time
            
            
