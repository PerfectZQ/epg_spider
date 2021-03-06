# -*- coding: utf-8 -*-
import codecs
import os

import scrapy_redis
from scrapy_redis.spiders import RedisSpider
from epg_spider.items import EPGItem
import json


class EpgRedisSpider(RedisSpider):
    name = 'epgspider_redis'
    allowed_domains = ["cctv.com"]
    redis_key = 'programList:starturls'

    def parse(self, response):
        request = response.request
        if 'proxy' in request.meta:
            print('proxy address in spider 1 :' + request.meta['proxy'])
        label_a = response.xpath("//h4/strong/a")
        program_type_text = label_a.xpath("./text()").extract()
        program_name_text = label_a.xpath("./font/text()").extract()
        if program_type_text and program_name_text:
            program_type_str = program_type_text[0]
            left_bracket_index = program_type_str.find('[')
            right_bracket_index = program_type_str.find(']')
            program_type = program_type_str[left_bracket_index + 1:right_bracket_index]
            program_name = program_name_text[0]
            print("spider 1 : " + program_name)
            epg = EPGItem(program_name=program_name, program_type=program_type)
            path = \
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.realpath(__file__)))) + '/data/program_type.json'
            with codecs.open(path, 'a+', 'utf-8') as json_file:
                json_file.write(json.dumps(dict(epg), ensure_ascii=False))
