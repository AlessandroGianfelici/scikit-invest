import pandas as pd
from invest.scoring import *
import os
from invest.loader import load_borsa_italiana_stocks_symbols
from invest.fundamental_analysis import main_fundamental_indicators
from invest.technical_analysis import detect_trend
from invest.scoring import compute_score, get_indicators
from invest import Stock
import pandas as pd
from invest.ratios import liquidity, efficiency, solvency, valuation

stock = Stock('ENI.MI')
main_fundamental_indicators(stock)


trend_magnitude, last_value_trendline = detect_trend(stock.hist.reset_index(),
                                                         verbose=1)