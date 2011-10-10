# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.conf import settings

from theses.spiders.usp import *

from pymongo import Connection
db = Connection().theses
db.fields.ensure_index('name', unique=True)
db.theses.ensure_index('author', unique=True)

class LowPassPipeline(object):
    def process_item(self, item, spider):
        if isinstance(spider, USPListAreasSpider):
            if item['size'] < settings['MINIMUM_SIZE']:
                raise DropItem('Size is lower than MINIMUM_SIZE (%d)' % settings['MINIMUM_SIZE'])
            return item
        return item

class DBDumpPipeline(object):
    def process_item(self, item, spider):
        try:
            if isinstance(spider, USPListAreasSpider):
                db.fields.insert(dict(item), safe=True)
            elif isinstance(spider, USPThesisSpider):
                db.theses.insert(dict(item), safe=True)
        except:
            raise DropItem('Item already added')
        return item
