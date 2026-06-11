# region imports
from AlgorithmImports import *
# endregion

class BootCampTask(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2017, 6, 1)
        self.set_end_date(2017, 6, 15)

        #1,2. Select IWM minute resolution data and set it to RAW normalization mode
        self.iwm = self.add_equity("IWM", Resolution.MINUTE)
        self.iwm.SetDataNormalizationMode(DataNormalizationMode.RAW)

    def on_data(self, data):

        #3. Place an order for 100 shares of IWM and print the average fill price
        if not self.portfolio.invested:

            self.market_order("IWM", 100)
        #4. Debug the average price of IWM
            self.debug(str(self.portfolio["IWM"].average_price))
            
