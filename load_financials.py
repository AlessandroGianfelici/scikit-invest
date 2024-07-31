
import os
import pandas as pd
from invest import Stock

data_path = os.path.join('invest', 'symbols')
it_stocks = pd.read_csv(os.path.join(data_path, 'euronext_milano.csv'))
for isin in it_stocks['Codice ISIN']:
    try:
        mystock = Stock(isin)
        mystock.yearly_financials
        mystock.quarterly_financials
    except: pass
    print(isin, ' DONE!')