import pandas as pd
import os

def load_linkedin():
    filepath = os.path.join(os.path.dirname(__file__), 'alternative', 'linkedin.csv')
    return pd.read_csv(filepath)

def load_symbols(filename : str):
    filepath = os.path.join(os.path.dirname(__file__), 'symbols', filename)
    return pd.read_csv(filepath).drop_duplicates().reset_index(drop=True)

def load_borsa_italiana_stocks_symbols():
    return load_symbols('borsa_italiana.csv')

def load_tokyo_stock_exchange_symbols():
    return load_symbols('tokyo_stock_exchange.csv')

def load_nasdaq_exchange_symbols():
    return load_symbols('NASDAQ.csv')
    

