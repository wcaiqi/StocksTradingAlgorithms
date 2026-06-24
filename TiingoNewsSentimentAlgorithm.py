# region imports
from AlgorithmImports import *
# endregion
from AlgorithmImports import *
class TiingoNewsSentimentAlgorithm(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2016, 11, 1)
        self.set_end_date(2025, 3, 1)  
        symbols = [Symbol.create(x, SecurityType.EQUITY, Market.USA) for x in ["AAPL", "NKE"]]
        self.set_universe_selection(ManualUniverseSelectionModel(symbols))
        self.set_alpha(NewsSentimentAlphaModel())
        self.set_portfolio_construction(EqualWeightingPortfolioConstructionModel()) 
        self.set_execution(ImmediateExecutionModel()) 
        self.set_risk_management(NullRiskManagementModel())

class NewsData():
    def __init__(self, symbol):
        self.symbol = symbol
        self.window = RollingWindow[float](100)  
        
class NewsSentimentAlphaModel(AlphaModel):
    
    def __init__(self): 
        self.news_data = {}

        self.word_scores = {
            "bad": -0.5, "good": 0.5, "negative": -0.5, 
            "great": 0.5, "growth": 0.5, "fail": -0.5, 
            "failed": -0.5, "success": 0.5, "nailed": 0.5,
            "beat": 0.5, "missed": -0.5, "profitable": 0.5,
            "beneficial": 0.5, "right": 0.5, "positive": 0.5, 
            "large":0.5, "attractive": 0.5, "sound": 0.5, 
            "excellent": 0.5, "wrong": -0.5, "unproductive": -0.5, 
            "lose": -0.5, "missing": -0.5, "mishandled": -0.5, 
            "un_lucrative": -0.5, "up": 0.5, "down": -0.5,
            "unproductive": -0.5, "poor": -0.5, "wrong": -0.5,
            "worthwhile": 0.5, "lucrative": 0.5, "solid": 0.5
        } 
                
    def update(self, algorithm, data):

        insights = []
        news = data.get(TiingoNews) 

        for article in news.values():
            words = article.description.lower().split(" ")
            score = sum([self.word_scores[word] for word in words
                if word in self.word_scores])
            
            #1. Get the underlying symbol and save to the variable symbol
            symbol = article.symbol.underlying
            
            #2. Add scores to the rolling window associated with its news_data symbol
            self.news_data[symbol].window.add(score)
            #3. Sum the rolling window scores, save to sentiment
            # If sentiment aggregate score for the time period is greater than 5, emit an up insight
            sentiment = sum(self.news_data[symbol].window)
            if sentiment > 5:
                insights.append(Insight.price(symbol, timedelta(1), InsightDirection.UP, None, None))
           
        return insights
    
    def on_securities_changed(self, algorithm, changes):

        for security in changes.added_securities:
            symbol = security.symbol
            news_asset = algorithm.add_data(TiingoNews, symbol)
            self.news_data[symbol] = NewsData(news_asset.symbol)

        for security in changes.removed_securities:
            news_data = self.news_data.pop(security.symbol, None)
            if news_data is not None:
                algorithm.remove_security(news_data.symbol)
