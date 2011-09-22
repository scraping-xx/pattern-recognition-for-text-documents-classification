from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.conf import settings

from urlparse import urljoin
from theses.items import *
from pymongo import Connection

import tempfile
import os


class USPSpider(BaseSpider):
    name = "usp"
    allowed_domains = ['teses.usp.br']
    start_urls = ['http://www.teses.usp.br/index.php?option=com_jumi&fileid=6&Itemid=61&lang=pt-br&pagina=1']
    base_url = 'http://www.teses.usp.br'

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        try:
            next_page = hxs.select('//div[@class="CorpoPaginacao"]/a[last()-1]/@href').extract()[0]
            yield Request(urljoin(self.base_url, next_page), callback=self.parse)
        except:
            print 'finished listing fields'
        for f in hxs.select('//div[@class="dadosLinha dadosCor1"] | //div[@class="dadosLinha dadosCor2"]'):
            item = FieldItem()
            item['name'] = f.select('.//div[@class="dadosAreaNome"]/a/text()').extract()[0]
            item['size'] = int(f.select('.//div[@class="dadosAreaNome"]/text()').extract()[0].replace(' (', '').replace(')', ''))
            item['type'] = f.select('.//div[@class="dadosAreaTipo"]/text()').extract()[0]
            item['url'] = urljoin(self.base_url, f.select('./div[@class="dadosAreaNome"]/a/@href').extract()[0])
            yield item

class USPListThesisSpider(BaseSpider):
    name = 'usp-list-thesis'
    allowed_domains = ['teses.usp.br']
    start_urls = []
    base_url = 'http://www.teses.usp.br'
    db = Connection().theses

    def start_requests(self):
        for f in settings['FIELDS']:
            field = self.db.fields.find_one({'name': f})
            yield Request(field['url'], callback=self.parse)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        try:
            next_page = hxs.select('//div[@class="CorpoPaginacao"]/a[last()-1]/@href').extract()[0]
            yield Request(urljoin(self.base_url, next_page), callback=self.parse)
        except:
            print 'finished listing thesis from field'
        for f in hxs.select('//div[@class="dadosLinha dadosCor1"] | //div[@class="dadosLinha dadosCor2"]'):
            item = ThesesItem()
            item['author'] = f.select('.//div[@class="dadosDocNome"]/a/text()').extract()[0]
            item['url'] = f.select('.//div[@class="dadosDocNome"]/a/@href').extract()[0]
            item['title'] = f.select('.//div[@class="dadosDocTitulo"]/text()').extract()[0]
            item['field'] = f.select('.//div[@class="dadosDocArea"]/a/text()').extract()[0]
            item['type'] = f.select('.//div[@class="dadosDocTipo"]/a/text()').extract()[0]
            item['dept'] = f.select('.//div[@class="dadosDocUnidade"]/a/text()').extract()[0]
            item['year'] = int(f.select('.//div[@class="dadosDocAno"]/a/text()').extract()[0])
            yield item

class USPThesisSpider(BaseSpider):
    name = 'usp-download-thesis'
    allowed_domains = [ 'teses.usp.br']
    start_urls = []
    base_url = 'http://www.teses.usp.br'
    db = Connection().theses

    def start_requests(self):
        for t in self.db.theses.find():
            if 'data' in t and len(t['data']) > 10:
                continue
            request = Request(t['url'], callback=self.parse)
            request.meta['thesis'] = t
            yield request

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        all_a = hxs.select('//a')
        for a in all_a:
            text = a.select('text()').extract()
            if len(text) > 0 and text[0].endswith('.pdf'):
                url = urljoin(self.base_url, a.select('@href').extract()[0])
                request = Request(url, callback=self.put_document)
                request.meta['thesis'] = response.meta['thesis']
                yield request

    def put_document(self, response):
        thesis = response.meta['thesis']

        t = tempfile.NamedTemporaryFile()
        t.write(response.body)
        t.flush()
        os.system('pdftotext %s' % t.name)

        thesis['data'] = open(t.name + '.txt').read()
        print 'Saving thesis', thesis['author'], len(thesis['data'])
        self.db.theses.save(thesis)
