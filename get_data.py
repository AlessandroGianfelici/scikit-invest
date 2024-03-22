#!/usr/bin/env python
# coding: utf-8

# In[18]:

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import invest
from invest.stock import Stock
from invest import loader
import time
import pandas as pd
from invest.scoring import compute_score, get_indicators
import os
from invest.utils import select_or_create

# In[12]:


ita_stocks = loader.load_borsa_italiana_stocks_symbols().drop_duplicates().reset_index(drop=1)


# In[13]:


try:
    1/0
    results = pd.read_excel('results.xlsx')
    already_done = set(results['code'])
except:
    results = pd.DataFrame()
    already_done = set()



for symbol in set(ita_stocks.SYMBOL) - already_done:
    mystock = Stock(symbol)
    time.sleep(1)
    print("°°°°   ", symbol, "°°°°   ")
    try:
        tmp = get_indicators(mystock)
        results = pd.concat([results,
                             tmp])
        mystock.hist.to_csv(os.path.join(select_or_create('time_series'),
                            symbol + '.csv'))
        results.to_excel('results.xlsx', index=0)
    except Exception as e:
        print(f"{e}: {e.__doc__}")
        pass


# In[ ]:


results#.to_excel('results.xlsx', index=0)


# In[ ]:


results = pd.read_excel('results.xlsx')


# In[ ]:


scores = compute_score(results.reset_index(drop=1)).set_index('code')


# In[ ]:


scores


# In[ ]:





