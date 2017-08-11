# -*- coding: utf-8 -*-
from scrapy import Request
from epg_spider.items import EPGItem
from epg_spider.oracle.db import OracleDB
import scrapy
import json


class EPGSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["search.cctv.com"]
    # 获取oracle数据库的连接
    conn = OracleDB.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT PROGRAM FROM GDI_SI_EPG_HIS_T')
    dataIter = cursor.__iter__()

    # 如果指定了URL，spider会调用 make_requests_from_url() 方法来创建 Request 对象
    # start_urls = ['http://search.cctv.com/search.php?type=video&']

    # 必须返回一个可迭代的对象（Iterable），当没有指定URL是，spider会调用此函数。
    def start_requests(self):
        for row in self.dataIter:
            program = row[0]
            url = 'http://search.cctv.com/search.php?qtext=%s&type=video' % program
            yield Request(url=url, callback=self.parse, meta={'program': program})

    def parse(self, response):
        label_a = response.xpath("//h4/strong/a")
        program_type = label_a.text()
        program_name = response.meta['program']
        epg = EPGItem(program_name=program_name, program_type=program_type)
        print(epg)

    # 读取文件
    def readFile(self, path):
        with open(path, 'r')as json_file:
            # 只能读取规范后的json文件,json对象或者json数组
            json.load(json_file)
