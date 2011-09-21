# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.conf import settings

class LowPassPipeline(object):
    def process_item(self, item, spider):
        print 'Process', item, spider
        if item['size'] < settings['MINIMUM_SIZE']:
            raise DropItem('Size is lower than MINIMUM_SIZE (%d < %d)' % (item['size'], settings['MINIMUM_SIZE']))
        return item

class ThesesPipeline(object):
    def process_item(self, item, spider):
        return item
