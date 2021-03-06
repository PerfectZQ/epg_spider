# -*- coding: utf-8 -*-
import random

import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings

from epg_spider.items import ProxyAddress


class ProxySpiderSwitch(object):
    """ 代理爬虫开关 """
    flag = True


class ProxySpider(scrapy.Spider):
    name = 'proxy_spider'
    allowed_domains = ['xicidaili.com']

    # start_urls = ['http://www.xicidaili.com/wt/']

    def start_requests(self):
        # 随机爬取前100页代理
        flag = True
        while flag:
            flag = ProxySpiderSwitch.flag
            page = random.choice(range(1, 100))
            url = 'http://www.xicidaili.com/wt/%d' % page
            request = Request(url=url)
            # 不走ProxyFilterMiddleware，不重新发送request，失败了就失败了
            request.meta['dont_retry'] = True
            # 代理池中为空的时候不等待代理，因为爬取代理的爬虫不使用爬取的代理
            request.meta['dont_wait_proxy'] = True
            request.dont_filter = True
            yield request

    def parse(self, response):
        """/tr[@class]/td[2]/text()"""
        # print(response.body)
        ips = response.xpath('//*[@id="ip_list"]/tr/td[2]/text()').extract()
        ports = response.xpath('//*[@id="ip_list"]/tr/td[3]/text()').extract()
        for ip, port in zip(ips, ports):
            yield ProxyAddress(proxy_address='http://%s:%s' % (ip, port))
