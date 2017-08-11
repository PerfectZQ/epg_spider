# -*- coding: utf-8 -*-
from spiders.epg import EPGSpider
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

settings = get_project_settings()
crawler = CrawlerProcess(settings)
crawler.crawl(EPGSpider)
crawler.start()
