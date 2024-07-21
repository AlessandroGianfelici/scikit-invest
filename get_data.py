from langchain_community.document_loaders import AsyncChromiumLoader
from bs4 import BeautifulSoup

def url_scheda(isin):
    return f"https://www.borsaitaliana.it/borsa/azioni/dati-completi.html?isin={isin}&lang=it"

loader = AsyncChromiumLoader([url_scheda('IT0001041000')])
html = loader.load()
soup = BeautifulSoup(str(html[0]), 'html.parser')
soup



