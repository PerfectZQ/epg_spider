# -*- coding: utf-8 -*-
import random

import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings

from epg_spider.items import ProxyAddress
import logging


class ProxySpiderSwitch(object):
    """ 代理爬虫开关 """
    flag = True


class ProxySpider(scrapy.Spider):
    name = 'qidianSpider'
    allowed_domains = ['qidian.com']

    # start_urls = ['http://www.xicidaili.com/wt/']

    def start_requests(self):
        request = Request(url="http://www.qidian.com")
        request.meta['dont_retry'] = True
        # 代理池中为空的时候不等待代理，因为爬取代理的爬虫不使用爬取的代理
        request.meta['dont_wait_proxy'] = True
        request.dont_filter = True
        yield request

    def parse(self, response):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        logger = logging.getLogger('qidianSpider')
        logger.info(str(response.headers))
        logger.info('-----------------------------')
        logger.info(str(response.body))

        # print(response.headers)
        # print('---------------')
        # print(response.body)
