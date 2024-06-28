import pandas as pd
import os
import yaml
import requests
#all_symbols = pd.read_csv("https://github.com/JerBouma/FinanceDatabase/raw/main/database/equities.csv")

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
    
def load_borsa_italiana():
    response = requests.get("https://github.com/JerBouma/FinanceDatabase/raw/main/database/equities.csv")
    if response.status_code == 200:
        with open("symbols.csv", "wb") as file:
            file.write(response.content)
            print("File downloaded successfully!")
    else:
        print("Failed to download the file.")
    all_stock = pd.read_csv("symbols.csv")
    italian_stock = all_stock.loc[all_stock['country'] == 'Italy']
    milan_exchange = italian_stock.loc[italian_stock['symbol'].str.contains('.MI')]
    return milan_exchange

def load_yaml(filename: str) -> dict:
    """Utility function to load a yaml file into a pyhon dict

    Parameters
    ----------
    filename : str
        fullpath of the yaml file

    Returns
    -------
    dict
    """
    assert filename.endswith("yaml") or filename.endswith(
        "yml"
    ), "Not a yaml extention!"
    with open(filename, "r", encoding="utf-8") as handler:
        return yaml.load(handler, Loader=yaml.FullLoader)
