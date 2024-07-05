from invest.scoring import compute_score, get_indicators
from invest import Stock
import pandas as pd
from invest.loader import load_borsa_italiana_stocks_symbols

symbols = load_borsa_italiana_stocks_symbols()

result = pd.DataFrame()

for symbol in symbols['SYMBOL']:
    try:
        mystock = Stock(symbol)
        result = (pd.concat([result,
                        get_indicators(mystock)]))
    except Exception as e:
        print(e, e.__doc__)
        raise

print("DONE!")