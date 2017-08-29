# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from epg_spider.spiders.epg_redis import EpgRedisSpider
from epg_spider.spiders.epg_redis2 import EpgRedisSpider2
from epg_spider.spiders.proxy_spider import ProxySpider

settings = get_project_settings()
crawler = CrawlerProcess(settings)
# 节目单爬虫
# crawler.crawl(EpgRedisSpider)
crawler.crawl(EpgRedisSpider2)
# 代理爬虫
# crawler.crawl(ProxySpider)
crawler.start()
