from langchain_community.document_loaders import AsyncChromiumLoader
from bs4 import BeautifulSoup
import pandas as pd
import requests
#from invest import Stock

#def isin2website(isin):
#    try:
#        mystock = Stock(isin)
#        return mystock.website
#    except Exception as e:
#        return f'{e} : {e.__doc__}'
    
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

def parse_links_from_html(html):

    # Crea un oggetto BeautifulSoup
    soup = BeautifulSoup(str(html[0]), 'html.parser')

    # Trova tutti i tag <a>
    links = soup.find_all('a')

    # Estrai gli attributi href dai tag <a>
    hrefs = [link.get('href') for link in links if link.get('href') is not None]
    hrefs = [link for link in hrefs if link.startswith("http")]
    hrefs = [link for link in hrefs if 'euronext' not in link]
    hrefs = [link for link in hrefs if 'linkedin' not in link]
    hrefs = [link for link in hrefs if 'borsaitaliana' not in link]
    print(hrefs)
    return hrefs

def get_company_website_link(isin):
    loader = AsyncChromiumLoader([url_financials(isin)])    
    html = loader.load()
    return parse_links_from_html(html)[0]

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