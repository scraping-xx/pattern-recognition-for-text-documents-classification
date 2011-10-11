# -*- coding: utf-8 -*-
# Scrapy settings for theses project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'ufcg-pattern-recog-AndreDieb'
BOT_VERSION = '1.0'
CONCURRENT_SPIDERS = 1
CONCURRENT_REQUESTS_PER_SPIDER = 1
CONCURRENT_REQUESTS = 1
CONCURRENT_ITEMS = 50
DOWNLOADER_DEBUG = True
DOWNLOAD_DELAY = 1
#LOG_LEVEL='INFO'

SPIDER_MODULES = ['theses.spiders']
NEWSPIDER_MODULE = 'theses.spiders'
DEFAULT_ITEM_CLASS = 'theses.items.ThesesItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = ['theses.pipelines.LowPassPipeline',
                  'theses.pipelines.DBDumpPipeline']

# Theses-specific settings
MINIMUM_SIZE = 50

# Tests #0
# > db.fields.find({size: {$lt: 60}}, {name: 1, size: 1})
FIELDS = ['Genética', 'Geotectônica', 'Engenharia de Sistemas', 'Engenharia Mecânica de Energia de Fluídos', 'Processamento de Sinais e Instrumentação']
