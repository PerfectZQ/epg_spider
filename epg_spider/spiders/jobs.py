# -*- coding: utf-8 -*-
import scrapy
import json
import cx_Oracle


class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["search.cctv.com"]
    start_urls = ['http://search.cctv.com/search.php?type=video&']

    def parse(self, response):
        response.xpath()

    # 读取文件
    def readFile(self, path):
        with open(path, 'r')as json_file:
            # 只能读取规范后的json文件,json对象或者json数组
            json.load(json_file)

    def getDataFromOracle(self):
        # 获取数据库连接
        # '用户名/密码/@数据库地址:端口号/ServiceName'
        conn = cx_Oracle.connect('DTSS_DB_USER/DTSS_DB_USER/@10.4.124.88:1621/lhytbill')