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
    return f"https://www.borsaitaliana.it/borsa/azioni/dati-completi.html?isin={isin}&lang=it"

def url_financials(isin):
    return f"https://www.borsaitaliana.it/borsa/azioni/profilo-societa-dettaglio.html?isin={isin}&lang=it"

def load_scheda(url_scheda):
    loader = AsyncChromiumLoader([url_scheda])
    html = loader.load()
    soup = BeautifulSoup(str(html[0]), 'html.parser')
    scheda_found = True
    ind = 0
    while not scheda_found:
        maybe_scheda = pd.read_html(str(soup.find_all("table")[ind]))[0]
        maybe_scheda = maybe_scheda.set_index(maybe_scheda.columns[0]).T
        scheda_found = ('Codice Isin' in maybe_scheda.columns)
        ind+=1
    return maybe_scheda


def load_financials(url_financials):
    loader = AsyncChromiumLoader([url_financials])
    html = loader.load()
    soup = BeautifulSoup(str(html[0]), 'html.parser')
    looking_for_financials = True
    ind = 0
    while looking_for_financials:
        maybe_financials = pd.read_html(str(soup.find_all("table")[ind]))[0]
        looking_for_financials = not('Millenium' in maybe_financials.columns)
        ind+=1
    return maybe_financials

def url_builder(stock):
    return stock