# -*- coding: utf-8 -*-
import logging
import random

import scrapy_redis
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.python import global_object_name

logger = logging.getLogger(__name__)


class ProxyMiddleware(object):
    """ 代理 download middleware，为不同类型的爬虫配置不同类型的代理 """

    def __init__(self, settings):
        proxy_pool = settings.get('PROXY_POOL')
        if not proxy_pool:
            raise NotConfigured
        self.proxy_pool = proxy_pool
        self.server = scrapy_redis.connection.get_redis_from_settings(settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Set the location of the proxy
        if spider.name == 'proxy_spider':
            request.meta['proxy'] = "http://10.4.125.134:819"
            # pass
        else:
            proxy_set = self.server.smembers(self.proxy_pool)
            # request.meta['proxy'] = random.choice(list(proxy_set))
            proxies = ['http://123.123.32.1:8080',
                       'http://123.123.32.2:8080',
                       'http://123.123.32.3:8080',
                       'http://123.123.32.4:8080',
                       'http://123.123.32.5:8080']
            proxy = random.choice(proxies)
            request.meta['proxy'] = proxy

            # Use the following lines if your proxy requires authentication
            # proxy_user_pass = "USERNAME:PASSWORD"
            # setup basic authentication for the proxy
            # encoded_user_pass = base64.b64encode(proxy_user_pass)
            # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass


class ProxyFilterMiddleware(object):
    """ 重新发送请求失败的URL，并统计代理IP的失效情况 """
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED') or not settings.get('PROXY_POOL') or not settings.get(
                'PROXY_FAILED_HASHMAP'):
            raise NotConfigured
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        # redis 客户端
        self.server = scrapy_redis.connection.get_redis_from_settings(settings)
        # 代理池
        self.proxy_pool = settings.get('PROXY_POOL')
        # 失败代理记录
        self.proxy_failed_hashmap = settings.get('PROXY_FAILED_HASHMAP')
        # 每个代理最多请求失败的次数
        self.proxy_failed_times = settings.get('PROXY_FAILED_TIMES')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        """
        当每个request通过下载中间件时，该方法被调用
        :param request: 处理的request
        :param spider: 该request对应的spider
        :return: 必须返回其中之一:
            1、None
            Scrapy 将继续处理该request，执行其他的中间件的相应方法，直到合适的下载器处理函
            数(download handler)被调用，该request被执行(其response被下载)
            2、Response
            Scrapy 将不会调用任何其他的 process_request() 或 process_exception() 方法，
            或相应地下载函数； 其将返回该response。已安装的中间件的 process_response()
            方法则会在每个response返回时被调用
            3、Request
            Scrapy 则停止调用 process_request方法并重新调度返回的request。当新返回的
            request被执行后，相应地中间件链将会根据下载的response被调用
            4、raise IgnoreRequest 异常
            则安装的下载中间件的 process_exception() 方法会被调用。如果没有任何一个方法处
            理该异常，则request的errback(Request.errback)方法会被调用。如果没有代码处理
            抛出的异常，则该异常被忽略且不记录(不同于其他异常那样)。
        """
        return None

    def process_response(self, request, response, spider):
        """

        :param request: response所对应的request
        :param response: 被处理的response
        :param spider: response所对应的spider
        :return: 必须返回以下之一：
            1、Response（可以是传入的Response，也可以是新的Response），
            继续被链中其他中间件的process_response方法处理
            2、Request
            中间件链停止，返回的Request会重新调度中间件链，相当于重新发送一个Request请求
            3、raise IgnoreRequest 异常
            调用request的errback(Request.errback)。 如果没有代码处理抛出的异常，
            则该异常被忽略且不记录(不同于其他异常那样)
        """
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider)
            # return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        """
        当下载处理器(download handler)或 process_request()(下载中间件)抛出异常(包括 IgnoreRequest 异常)时，
        Scrapy调用 process_exception()
        :param request: 产生异常的request
        :param exception: 抛出的异常
        :param spider: request对应的spider
        :return:应该返回以下之一：
        应该返回以下之一:
            1、None
            Scrapy将会继续处理该异常，接着调用已安装的其他中间件的 process_exception() 方法，
            直到所有中间件都被调用完毕，则调用默认的异常处理。
            2、Response
            则已安装的中间件链的 process_response() 方法被调用。Scrapy将不会调用任何其他中间
            件的 process_exception() 方法。
            3、Request
            则返回的request将会被重新调用下载。这将停止中间件的 process_exception() 方法执行，
            就如返回一个response的那样。
        """
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        stats = spider.crawler.stats
        logger.debug(
            "Retrying %(request)s, %(reason)s, and this request has failed %(retries)d times",
            {'request': request, 'retries': retries, 'reason': reason},
            extra={'spider': spider})
        proxy = request.meta['proxy']
        # 记录代理失败次数
        failed_times = self.server.hget(self.proxy_failed_hashmap, proxy)
        if failed_times < self.proxy_failed_times:
            self.server.hset(self.proxy_failed_hashmap, proxy, failed_times + 1)
            logger.debug(
                "current proxy is %(proxy)s, this proxy has failed %(failed_times)d times",
                {'request': request, 'retries': retries, 'reason': reason},
                extra={'spider': spider})
        else:
            self.server.srem(self.proxy_pool)
            logger.debug(
                "current proxy is %(proxy)s, this proxy has failed %(failed_times)d times, removed from proxy pool",
                {'request': request, 'retries': retries, 'reason': reason},
                extra={'spider': spider})

        retry_request = request.copy()
        retry_request.meta['retry_times'] = retries
        # 不会被当成重复URL过滤掉
        retry_request.dont_filter = True
        retry_request.priority = request.priority + self.priority_adjust

        if isinstance(reason, Exception):
            reason = global_object_name(reason.__class__)

        stats.inc_value('retry/count')
        stats.inc_value('retry/reason_count/%s' % reason)
        return retry_request
