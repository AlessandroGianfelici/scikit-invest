from invest.data_loader import borsa_italiana, loader
import pandas as pd
import os

euronext_milan =  pd.read_csv(os.path.join('invest', 'symbols', 'euronext_milano.csv')).set_index('Codice ISIN')[['Nome']].to_dict()['Nome']

__all__ = ['borsa_italiana', 'loader', 'euronext_milan']
