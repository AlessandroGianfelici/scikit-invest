import pandas as pd
from invest.scoring import *
import os

last_file = max(list(filter(lambda x : (x.startswith('risultati') and x.endswith('.xlsx')), os.listdir())))
indicatori = pd.read_excel(last_file)
indicatori = compute_score(indicatori.set_index('code')).sort_values(by='OVERALL_SCORE', ascending=False)
indicatori.drop(columns='name')
compute_score(indicatori.set_index('code'))