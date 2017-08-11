# -*- coding: utf-8 -*-
import cx_Oracle


class OracleDB:
    def __init__(self, ):
        pass

    @staticmethod
    def get_connection():
        # '用户名/密码@数据库地址:端口号/ServiceName'
        return cx_Oracle.connect('DTSS_DB_USER/DTSS_DB_USER@10.4.124.88:1621/lhytbill')
        # 或者
        # return cx_Oracle.connect('DTSS_DB_USER', 'DTSS_DB_USER', '10.4.124.88:1621/lhytbill')
