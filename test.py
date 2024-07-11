from invest.scoring import compute_score, get_indicators
from invest import Stock
import pandas as pd
from invest.data_loader.loader import load_borsa_italiana_stocks_symbols

symbols = load_borsa_italiana_stocks_symbols()

result = pd.DataFrame()
mystock = Stock('KK.MI')
result = pd.concat([result,
                        get_indicators(mystock)])

#for symbol in symbols['SYMBOL']:
#    try:
#        mystock = Stock(symbol)
#        result = (pd.concat([result,
#                             get_indicators(mystock)]))
#    except Exception as e:
#        print(e, e.__doc__)
#result.to_excel('risultati.xlsx', index=0)
#compute_score(result.reset_index(drop=1)).to_excel('scores.xlsx', index=0)
#print("DONE!")