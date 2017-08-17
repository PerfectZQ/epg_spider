# -*- coding: utf-8 -*-
import os
import csv

# 在哪个文件夹下调用就显示哪个文件夹
pwd = os.getcwd()
# 获取当前文件真正所在的目录
pwd = os.path.split(os.path.realpath(__file__))[0]
# 获取当前文件的真是路径包含当前文件的文件名
pwd = os.path.realpath(__file__)
print('the path is : ' + pwd)
