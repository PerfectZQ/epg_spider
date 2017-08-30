# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
import scrapy_redis
from scrapy.exceptions import NotConfigured
from twisted.internet.threads import deferToThread


class ProxyPipeline(object):
    """ 将爬取的proxy存入redis集合 """

    def __init__(self, server, proxy_pool, proxy_failed_hashmap):
        # redis客户端
        self.server = server
        # 代理池
        self.proxy_pool = proxy_pool
        # 失败代理记录
        self.proxy_failed_hashmap = proxy_failed_hashmap

    @classmethod
    def from_settings(cls, settings):
        """ cls 代表当前类本身，cls(args*)相当于调用当前类的__init__(args*)方法"""
        if not settings.get('PROXY_POOL') or not settings.get('PROXY_FAILED_HASHMAP'):
            raise NotConfigured
        params = {
            'server': scrapy_redis.connection.get_redis_from_settings(settings),
            'proxy_pool': settings.get('PROXY_POOL'),
            'proxy_failed_hashmap': settings.get('PROXY_FAILED_HASHMAP')
        }
        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        if spider.name == 'proxy_spider':
            proxy = item['proxy_address']
            proxies = {'http': proxy}
            headers = {
                'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8'
            }
            try:
                """ 延迟大于3秒的代理就算超时 """
                status_code = requests.get('http://search.cctv.com/', proxies=proxies, timeout=3,
                                           headers=headers).status_code
            except:
                """ I just don't want to see the fucking errors """
                pass
            else:
                if status_code == 200:
                    print(proxy + ' test success')
                    self.server.sadd('proxy_set', proxy)
                    # 并将代理的失败次数置为0
                    self.server.hset('failed_proxy_hm', proxy, 0)
                    return item

    """
    def process_item(self, item, spider):
        proxy = item['proxy_address']
        proxies = {'http': proxy}
        if requests.get('www.baidu.com', proxies=proxies, timeout=2).status_code == 200:
            pool = redis.ConnectionPool(host='127.0.0.1', port=7001)
            r = redis.Redis(connection_pool=pool)
            r.sadd('proxy_set', proxy)
        else:
            print(proxy + 'connected failed')
    """
