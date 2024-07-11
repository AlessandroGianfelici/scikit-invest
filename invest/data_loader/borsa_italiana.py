from langchain_community.document_loaders import AsyncChromiumLoader
from bs4 import BeautifulSoup
import pandas as pd
import requests

def load_isin_list():
    url = f"https://www.milanofinanza.it/quotazioni/ricerca/listino-completo-2ae?campoord=&ord=&alias=&selettorecod=&pag=0"
    html_code = requests.get(url)
    soup = BeautifulSoup(html_code.content, 'html.parser')
    tables = pd.read_html(str(soup.find("table")))[0]
    return tables.loc[tables['Codice ISIN'].str.startswith('IT')].reset_index(drop=1)

def url_scheda(isin):
    return f"https://www.borsaitaliana.it/borsa/azioni/scheda/{isin}.html?lang=it"

def url_financials(isin):
    return f"https://www.borsaitaliana.it/borsa/azioni/profilo-societa-dettaglio.html?isin={isin}&lang=it"

def load_isin_alfa_transcode(url_scheda):
    loader = AsyncChromiumLoader([url_scheda])
    html = loader.load()
    soup = BeautifulSoup(str(html[0]), 'html.parser')
    return pd.read_html(str(soup.find_all("table")[1]))[0].set_index(0).T

def load_financials(url_financials):
    loader = AsyncChromiumLoader([url_financials])
    html = loader.load()
    soup = BeautifulSoup(str(html[0]), 'html.parser')
    return pd.read_html(str(soup.find_all("table")[1]))[0]