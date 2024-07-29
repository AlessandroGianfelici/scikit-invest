from langchain_community.document_loaders import AsyncChromiumLoader
from bs4 import BeautifulSoup

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
    return hrefs

def url_financials(isin):
    return f"https://www.borsaitaliana.it/borsa/azioni/profilo-societa-dettaglio.html?isin={isin}&lang=it"




