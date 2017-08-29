# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from epg_spider.items import EPGItem


class EpgRedisSpider2(RedisSpider):
    name = 'epgspider_redis2'
    allowed_domains = ["cctv.com"]
    redis_key = 'test:starturl'

    def parse(self, response):
        label_a = response.xpath("//h4/strong/a")
        program_type_text = label_a.xpath("./text()").extract()
        program_name_text = label_a.xpath("./font/text()").extract()
        if program_type_text and program_name_text:
            program_type_str = program_type_text[0]
            left_bracket_index = program_type_str.find('[')
            right_bracket_index = program_type_str.find(']')
            program_type = program_type_str[left_bracket_index + 1:right_bracket_index]
            program_name = program_name_text[0]
            print("spider 2 : " + program_name + ':' + program_type)
            epg = EPGItem(program_name=program_name, program_type=program_type)
            # 继承自 RedisMixin(object)
            self.server.hmset('program_type_list', dict(epg))
