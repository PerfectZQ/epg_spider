# -*- coding: utf-8 -*-
import os
import csv
import random

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPProxyAuth

'''
# 在哪个文件夹下调用就显示哪个文件夹
pwd = os.getcwd()
# 获取当前文件真正所在的目录
pwd = os.path.split(os.path.realpath(__file__))[0]
# 获取当前文件的真是路径包含当前文件的文件名
pwd = os.path.realpath(__file__)
print('the path is : ' + pwd)
'''

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}


def getProxy():
    url = 'http://api.xicidaili.com/free2016.txt'
    proxy_str = '''http://192.168.107.27:8080'''
    proxies = {"http": proxy_str, "https": proxy_str}
    # url = 'http://www.xicidaili.com/nt/%d' % pageproxies
    session = requests.session()
    session.proxies = proxies
    session.auth = HTTPProxyAuth('zhang_qiang_neu', '3edc#EDC')
    session.trust_env = False
    html = session.get(url).content
    # html = requests.request('GET', url, headers=headers, proxies=proxies)
    print(html)


getProxy()
