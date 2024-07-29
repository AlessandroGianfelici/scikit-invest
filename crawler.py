import scrapy
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import os
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO

def file_folder_exists(path: str):
    """
    Return True if a file or folder exists.
    :param path: the full path to be checked
    :type path: str
    """
    try:
        os.stat(path)
        return True
    except:
        return False


def select_or_create(path: str):
    """
    Check if a folder exists. If it doesn't, it create the folder.
    :param path: path to be selected
    :type path: str
    """
    if not file_folder_exists(path):
        os.makedirs(path)
    return path

def get_domain_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc


data_path = os.path.join('invest', 'symbols', 'company_url_table.csv')
start_urls = pd.read_csv(data_path)
start_urls['domain'] = start_urls['website'].apply(get_domain_from_url)

class PdfSpider(scrapy.Spider):
    name = 'pdf_spider'

    def __init__(self, domain_table = start_urls, *args, **kwargs):
        super(PdfSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls['website'].to_list()
        self.allowed_domains = start_urls['domain'].to_list()
        self.folders = start_urls['isin'].to_list()
        self.keywords = ['EBIT']


    def parse(self, response):
        le = LinkExtractor(allow=(), tags=('a', 'area'), attrs=('href',), deny_extensions=())
        links = le.extract_links(response)
        for link in links:
            if link.url.endswith('.pdf'):
                yield scrapy.Request(link.url, callback=self.save_pdf)
            else:
                yield scrapy.Request(link.url, callback=self.parse)

    def filter_pdf(self, response):
        # Leggi il contenuto del PDF
        pdf_stream = BytesIO(response.body)
        pdf_reader = PdfReader(pdf_stream)

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            print('\n\n\n\n\n\n\n')
            print(text)
            print('\n\n\n\n\n\n\n')
            # Controlla se il testo contiene una delle parole chiave
            if any(keyword in text for keyword in self.keywords):
                self.save_pdf(response)
                pdf_stream.close()
                return

    def save_pdf(self, response):
        path = urlparse(response.url).path

        domain = urlparse(response.url).netloc
        folder_index = self.allowed_domains.index(domain)
        select_or_create('data')
        folder_name = select_or_create(os.path.join('data', self.folders[folder_index]))

        path = urlparse(response.url).path
        file_name = os.path.basename(path)
        file_path = os.path.join(folder_name, file_name)

        self.logger.info(f"Saving PDF {file_name} to {folder_name}")
        with open(file_path, 'wb') as f:
            f.write(response.body)