# -*- coding: utf-8 -*-
import codecs
import os

import scrapy_redis
from scrapy_redis.spiders import RedisSpider
from epg_spider.items import EPGItem
import json


class EpgRedisSpider2(RedisSpider):
    name = 'epgspider_redis2'
    allowed_domains = ["cctv.com"]
    redis_key = 'testepg'

    def parse(self, response):
        # label_a = response.xpath("//h4/strong/a/text()").extract()
        if response.status != 200:
            """ 将请求失败的URL写回redis中，并将请求失败的IP代理从代理池中清空 """
            settings = self.settings
            server = scrapy_redis.connection.get_redis_from_settings(settings)
            url = response.request.url
            server.lpush('programList:starturls', url)
            print('spider 2 -> requestURL: ' + url + '，请求失败，放回 redis队列中，等待重新爬取。')
            proxy = response.request.meta['proxy']
            server.srem("proxy_set", proxy)
            print('spider 2 -> 代理: ' + proxy + ' 失效，已删除。')
        else:
            request = response.request
            if 'proxy' in request.meta:
                print('proxy address in spider 2 :' + request.meta['proxy'])
            label_a = response.xpath("//h4/strong/a")
            program_type_text = label_a.xpath("./text()").extract()
            program_name_text = label_a.xpath("./font/text()").extract()
            if program_type_text and program_name_text:
                program_type_str = program_type_text[0]
                left_bracket_index = program_type_str.find('[')
                right_bracket_index = program_type_str.find(']')
                program_type = program_type_str[left_bracket_index + 1:right_bracket_index]
                program_name = program_name_text[0]
                print("spider 2 : " + program_name)
                epg = EPGItem(program_name=program_name, program_type=program_type)
                path = \
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(
                                os.path.realpath(__file__)))) + '/data/program_type.json'
                with codecs.open(path, 'a+', 'utf-8') as json_file:
                    json_file.write(json.dumps(dict(epg), ensure_ascii=False))
