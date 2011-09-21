# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ThesesItem(Item):
    author = Field()
    url = Field()
    title = Field()
    field = Field()
    type = Field()
    dept = Field()
    year = Field()
    data = Field()

class FieldItem(Item):
    name = Field()
    size = Field()
    type = Field()
    url = Field()
