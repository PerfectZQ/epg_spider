# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
import scrapy_redis
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread


class EpgSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


default_serialize = ScrapyJSONEncoder().encode


class ProxyPipeline(object):
    """将存活的proxy存入redis"""

    def __init__(self, server):
        """Initialize pipeline.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        serialize_func : callable
            Items serializer function.

        """
        self.server = server

    @classmethod
    def from_settings(cls, settings):
        """ cls 代表当前类本身，cls(args*)相当于调用当前类的__init__(args*)方法"""
        params = {
            'server': scrapy_redis.connection.get_redis_from_settings(settings),
        }
        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        key = 'proxy_set_test'
        proxy = item['proxy_address']
        proxies = {'http': proxy}
        try:
            """ 延迟大于2秒的代理就算超时 """
            status_code = requests.get('http://search.cctv.com/', proxies=proxies, timeout=2).status_code
        except:
            """ I don't want to see the fucking errors """
            pass
        else:
            if status_code == 200:
                print(proxy + ' test success')
                self.server.sadd(key, proxy)
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
