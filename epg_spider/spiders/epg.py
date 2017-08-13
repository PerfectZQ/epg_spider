# -*- coding: utf-8 -*-
from scrapy import Request
from epg_spider.items import EPGItem
from epg_spider.oracle.db import OracleDB
import scrapy
import json


class EPGSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["cctv.com"]
    # 获取oracle数据库的连接
    conn = OracleDB.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT PROGRAM FROM GDI_SI_EPG_HIS_T WHERE ROWNUM<50')
    dataIter = cursor.__iter__()

    # 如果指定了URL，spider会调用 make_requests_from_url() 方法来创建 Request 对象
    # start_urls = ['http://search.cctv.com/search.php?type=video&']

    # 必须返回一个可迭代的对象（Iterable），当没有指定URL是，spider会调用此函数。
    def start_requests(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'search.cctv.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        for row in self.dataIter:
            program = row[0]
            url = 'http://search.cctv.com/search.php?qtext=%s&type=video' % program
            yield Request(url=url, callback=self.parse, headers=headers, meta={'program': program})

    def parse(self, response):
        label_a = response.xpath("//h4/strong/a/text()").extract()
        if label_a:
            program_type_str = label_a[0]
            left_bracket_index = program_type_str.find('[')
            right_bracket_index = program_type_str.find(']')
            program_type = program_type_str[left_bracket_index + 1:right_bracket_index]
            program_name = response.meta['program']
            epg = EPGItem(program_name=program_name, program_type=program_type)
            with open('../../data/program_type.json', 'a+') as json_file:
                json_file.write(json.dumps(dict(epg)))

    # 读取文件
    def readFile(self, path):
        with open(path, 'r')as json_file:
            # 只能读取规范后的json文件,json对象或者json数组
            json.load(json_file)

    def write2DB(self):
        pass