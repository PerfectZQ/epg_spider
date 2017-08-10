# -*- coding: utf-8 -*-
import cx_Oracle


def getConnection():
    # 获取数据库连接
    # '用户名/密码@数据库地址:端口号/ServiceName'
    return cx_Oracle.connect('DTSS_DB_USER/DTSS_DB_USER@10.4.124.88:1621/lhytbill')
    # 或者
    # return cx_Oracle.connect('DTSS_DB_USER', 'DTSS_DB_USER', '10.4.124.88:1621/lhytbill')


conn = getConnection()
cursor = conn.cursor()
cursor.execute('SELECT DISTINCT PROGRAM FROM GDI_SI_EPG_HIS_T')
results = cursor.fetchall()
# row是元组类型
for row in results:
    print(row[0])
cursor.close()
conn.close()
