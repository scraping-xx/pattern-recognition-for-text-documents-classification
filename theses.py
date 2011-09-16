# -*- coding: utf-8 -*-

import urlparse

from lxml.cssselect import CSSSelector
from lxml import etree, html

class Thesis(object):
    author_ = CSSSelector("div[class='dadosDocNome'] a")
    title_ = CSSSelector("div[class='dadosDocTitulo']")
    area_ = CSSSelector("div[class='dadosDocArea'] a")
    type_ = CSSSelector("div[class='dadosDocTipo'] a")
    dept_ = CSSSelector("div[class='dadosDocUnidade'] a")
    year_ = CSSSelector("div[class='dadosDocAno'] a")

    @staticmethod
    def is_valid_masters_thesis(r):
        try:
            return 'Mestrado' in Thesis.type_(r)[0].text
        except Exception, e:
            print 'nao', e
            return False

    @staticmethod
    def parse(r):
        t = Thesis()

        # Author and download url
        author = t.author_(r)[0]
        t.author = author.text
        t.url = author.attrib['href']

        # Area
        t.area = t.area_(r)[0].text

        # Department
        t.dept = t.dept_(r)[0].text

        # Year
        t.year = t.year_(r)[0].text
        return t

    def __str__(self):
        return '<Thesis author="%s" url="%s">' % (self.author, self.url)

class ThesisSpider(object):
    masters_main = 'http://www.teses.usp.br/index.php?option=com_jumi&fileid=11&Itemid=76&lang=pt-br'
    doctorate_main = 'http://www.teses.usp.br/index.php?option=com_jumi&fileid=12&Itemid=77&lang=pt-br'
    areas_main = 'http://www.teses.usp.br/index.php?option=com_jumi&fileid=6&Itemid=61&lang=pt-br'

    def fetch_and_parse(self, url):
        return html.parse(url)

    def areas(self, min_thesis=100, page=1):
        result_sel = CSSSelector("div[class='dadosLinha dadosCor1'], div[class='dadosLinha dadosCor2']")
        name_ = CSSSelector("div[class='dadosAreaNome']")
        type_ = CSSSelector("div[class='dadosAreaTipo']")
        dept_ = CSSSelector("div[class='dadosAreaUnidade'] a")

        url = self.areas_main + '&pagina=%d' % page
        page = self.fetch_and_parse(url)

        for r in result_sel(page):
            area = {}
            name = name_(r)[0]
            area['size'] = int(name.text_content().split(' ')[-1].split('(')[1].replace(')', ''))
            if area['size'] < min_thesis:
                continue
            area['url'] = name.find('a').attrib['href']
            area['name'] = name.find('a').text
            yield area

    def get_masters_thesis(self, page=None):
        url = self.masters_main
        result_sel = CSSSelector("div[class='dadosLinha dadosCor1'], div[class='dadosLinha dadosCor2']")

        if page is not None:
            url += '&pagina=%d' % page

        results_page = self.fetch_and_parse(url)
        docs = []
        for r in result_sel(results_page):
            if Thesis.is_valid_masters_thesis(r):
                docs.append(Thesis.parse(r))
        return docs

if __name__ == '__main__':
    spider = ThesisSpider()
#    for t in spider.get_masters_thesis():
#        print unicode(t)
    for i in range(10):
        for a in spider.areas(page=i):
            print a['name'], a['size']
