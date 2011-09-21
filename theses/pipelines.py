# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.conf import settings

from theses.spiders.usp import *

from pymongo import Connection
db = Connection().theses
db.fields.ensure_index('name')
db.theses.ensure_index('author')

class LowPassPipeline(object):
    def process_item(self, item, spider):
        if isinstance(spider, USPSpider):
            if item['size'] < settings['MINIMUM_SIZE']:
                raise DropItem('Size is lower than MINIMUM_SIZE (%d < %d)' % (item['size'], settings['MINIMUM_SIZE']))
            return item
        return item

class DBDumpPipeline(object):
    def process_item(self, item, spider):
        if isinstance(spider, USPSpider):
            db.fields.insert(dict(item))
        elif isinstance(spider, USPThesisSpider):
            db.theses.insert(dict(item))

class ThesesPipeline(object):
    def process_item(self, item, spider):
        return item
