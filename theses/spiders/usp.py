from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.conf import settings

from scrapy import log

from urlparse import urljoin
from theses.items import *
from pymongo import Connection

import tempfile
import os


class USPListAreasSpider(BaseSpider):
    """ Lists USP thesis areas (e.g. biology, mechanical engineering, architecture, etc)
    """
    name = "usp-list-areas"
    allowed_domains = ['teses.usp.br']
    start_urls = ['http://www.teses.usp.br/index.php?option=com_jumi&fileid=6&Itemid=61&lang=pt-br&pagina=1']
    base_url = 'http://www.teses.usp.br'

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        try:
            next_page = hxs.select('//div[@class="CorpoPaginacao"]/a[last()-1]/@href').extract()[0]
            yield Request(urljoin(self.base_url, next_page), callback=self.parse)
        except:
            pass
        for f in hxs.select('//div[@class="dadosLinha dadosCor1"] | //div[@class="dadosLinha dadosCor2"]'):
            item = FieldItem()
            item['name'] = f.select('.//div[@class="dadosAreaNome"]/a/text()').extract()[0]
            item['size'] = int(f.select('.//div[@class="dadosAreaNome"]/text()').extract()[0].replace(' (', '').replace(')', ''))
            item['type'] = f.select('.//div[@class="dadosAreaTipo"]/text()').extract()[0]
            item['url'] = urljoin(self.base_url, f.select('./div[@class="dadosAreaNome"]/a/@href').extract()[0])
            yield item

class USPThesisSpider(BaseSpider):
    """ Retrieve theses info.
    """
    name = 'usp-list-theses'
    allowed_domains = ['teses.usp.br']
    start_urls = []
    base_url = 'http://www.teses.usp.br'
    db = Connection().theses

    def start_requests(self):
        for f in settings['FIELDS']:
            field = self.db.fields.find_one({'name': f})
            print 'Creating request for ', field['url']
            yield Request(field['url'], callback=self.parse_theses_list)

    def parse_theses_list(self, response):
        hxs = HtmlXPathSelector(response)
        print 'Parsing list'
        try:
            next_page = hxs.select('//div[@class="CorpoPaginacao"]/a[last()-1]/@href').extract()[0]
            yield Request(urljoin(self.base_url, next_page), callback=self.parse_theses_list)
        except:
            print 'Finished listing thesis from field'
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

class USPDownloadThesisSpider(BaseSpider):
    """ Retrieve theses docs.
    """
    name = 'usp-theses-docs'
    allowed_domains = ['teses.usp.br']
    start_urls = []
    base_url = 'http://www.teses.usp.br'
    db = Connection().theses

    def start_requests(self):
        for t in self.db.theses.find():
            if 'data' in t and len(t['data']) > 0:
                continue
            # Create a request to download the pdf and process it
            req = Request(urljoin(self.base_url, t['url']), callback=self.parse_thesis_spec)
            req.meta['thesis'] = t
            yield req

    def parse_thesis_spec(self, response):
        hxs = HtmlXPathSelector(response)
        thesis = response.meta['thesis']

        # Pdf download
        all_a = hxs.select('//a')
        urls = []
        for a in all_a:
            text = a.select('text()').extract()
            if len(text) > 0 and text[0].endswith('.pdf'):
                urls.append(a.select('@href').extract()[0])

        if len(urls) == 0:
            # Invalidate damned fragmented theses with many pdfs
            log.msg('Invalid thesis, no files', level=log.WARNING, spider=self)
            return
        elif len(urls) > 1:
            log.msg('Many pdfs, considering only first', level=log.WARNING, spider=self)

        url = urljoin(self.base_url, urls[0])
        log.msg('Downloading pdf from %s' % url, level=log.INFO, spider=self)
        request = Request(url, callback=self.parse_doc)
        request.meta['thesis'] = response.meta['thesis']
        yield request

    def parse_doc(self, response):
        thesis = response.meta['thesis']
        log.msg('Parsing pdf for thesis %s' % thesis['author'], level=log.DEBUG, spider=self)

        t = tempfile.NamedTemporaryFile()
        t.write(response.body)
        t.flush()
        os.system('pdftotext %s' % t.name)

        thesis['data'] = open(t.name + '.txt').read()
        log.msg('Downloaded thesis (len=%d)' % (len(thesis['data'])), level=log.DEBUG, spider=self)
        # Save it back
        self.db.theses.save(thesis)
