from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from urlparse import urljoin

from theses.items import *

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
        for f in hxs.select('//div[@class="dadosLinha dadosCor1"] | .//div[@class="dadosLinha dadosCor2"]'):
            item = FieldItem()
            item['name'] = f.select('.//div[@class="dadosAreaNome"]/a/text()').extract()[0]
            item['size'] = int(f.select('.//div[@class="dadosAreaNome"]/text()').extract()[0].replace(' (', '').replace(')', ''))
            item['type'] = f.select('.//div[@class="dadosAreaTipo"]/text()').extract()[0]
            item['url'] = urljoin(self.base_url, f.select('./div[@class="dadosAreaNome"]/a/@href').extract()[0])
            yield item
