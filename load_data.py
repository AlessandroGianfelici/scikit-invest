
from invest.data_loader.borsa_italiana import isin2website, load_isin_list, load_financials, load_scheda, url_scheda, url_financials
import os
import pandas as pd
from invest.utils import file_folder_exists, select_or_create

it_stocks = load_isin_list()

data_path = os.path.join('invest', 'symbols')
transcode_path = select_or_create(os.path.join(data_path, 'scheda'))
financials_path = select_or_create(os.path.join(data_path, 'financials'))

it_stocks.to_csv(os.path.join(data_path, 'euronext_milano.csv'))

for isin in it_stocks['Codice ISIN']:
    print(isin)
    transcode_table_path = os.path.join(transcode_path, f'{isin}.csv')
    financials_table_path = os.path.join(financials_path, f'{isin}.csv')
    if not(file_folder_exists(transcode_table_path)):
        try:
            transcode_table = load_scheda(url_scheda(isin))
            transcode_table.to_csv(transcode_table_path, index=0)
        except Exception as e:
            print(e, e.__doc__)
            pass
    if not(file_folder_exists(financials_table_path)):
        try:
            financials_table = load_financials(url_financials(isin))
            financials_table.to_csv(financials_table_path, index=0)
        except Exception as e:
            print(e, e.__doc__)
            pass

isin_alpha_transcode = pd.concat(map(lambda x : pd.read_csv(os.path.join(transcode_path, x)), os.listdir(transcode_path)))
isin_alpha_transcode['yahoo_code'] = isin_alpha_transcode['Codice Alfanumerico'].apply(lambda x : f"{x}.MI")
isin_alpha_transcode[['Codice Isin', 'Codice Alfanumerico', 'yahoo_code']].to_csv(os.path.join(data_path, 'milan_isin_transcode.csv'), index=0)

company_website = it_stocks[['Nome', 'Codice ISIN']].copy()
company_website['website'] = it_stocks['Codice ISIN'].apply(isin2website)
company_website.to_csv(os.path.join(data_path, 'company_websites.csv'), index=0)