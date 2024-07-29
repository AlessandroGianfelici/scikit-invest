import scrapy
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import os

start_urls

class PdfSpider(scrapy.Spider):
    name = 'pdf_spider'

    def __init__(self, domains=None, *args, **kwargs):
        super(PdfSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        self.allowed_domains = [domain for domain in domains.split(',')]

    def parse(self, response):
        le = LinkExtractor(allow=(), tags=('a', 'area'), attrs=('href',), deny_extensions=())
        links = le.extract_links(response)
        for link in links:
            if link.url.endswith('.pdf'):
                yield scrapy.Request(link.url, callback=self.save_pdf)
            else:
                yield scrapy.Request(link.url, callback=self.parse)

    def save_pdf(self, response):
        path = urlparse(response.url).path
        file_name = os.path.basename(path)
        self.logger.info(f"Saving PDF {file_name}")
        with open(file_name, 'wb') as f:
            f.write(response.body)