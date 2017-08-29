# -*- coding: utf-8 -*-
import scrapy
import scrapy_redis
from scrapy import Request

from epg_spider.items import ProxyAddress


class ProxySpider(scrapy.Spider):
    name = 'proxy_spider'
    allowed_domains = ['xicidaili.com']

    # start_urls = ['http://www.xicidaili.com/wt/']

    def start_requests(self):
        # """ 开始爬取新的代理时先清空redis中的代理数据 """
        # settings = self.settings
        # server = scrapy_redis.connection.get_redis_from_settings(settings)
        # server.delete('proxy_set_test')
        # 爬取前10页代理
        for page in xrange(1, 10):
            url = 'http://www.xicidaili.com/wt/%d' % page
            yield Request(url=url)

    def parse(self, response):
        """/tr[@class]/td[2]/text()"""
        # print(response.body)
        ips = response.xpath('//*[@id="ip_list"]/tr/td[2]/text()').extract()
        ports = response.xpath('//*[@id="ip_list"]/tr/td[3]/text()').extract()
        for ip, port in zip(ips, ports):
            yield ProxyAddress(proxy_address='http://%s:%s' % (ip, port))
