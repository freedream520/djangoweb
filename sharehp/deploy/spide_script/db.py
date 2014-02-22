# -*- coding: utf-8 -*-
from datetime import datetime
import MySQLdb
import hashlib


class SpideResource:
    def __init__(self, title, type, content, origin):
        # 资源标题
        self.title = title
        # 资源类型
        self.type = type
        # 资源内容 {'name': ..., 'normal_path': ..., 'thumbnail_path': ..., 'url': ...}
        self.content = content
        # 资源原始url
        self.origin = origin
        # 资源MD5（防止抓取重复的资源）
        self.md5 = hashlib.md5(origin).hexdigest()



def save(resource):
    conn = None
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='sharehp', charset='utf8')
        cursor = conn.cursor()
        sql = 'INSERT INTO sharehp_spide_resource ' \
              '(gmt_create, title, type, content, origin, md5, status) VALUES(%s, %s, %s, %s, %s, %s, %s)'

        cursor.execute(sql, (datetime.now(),
                             resource.title.encode("utf8"),
                             resource.type,
                             resource.content,
                             resource.origin,
                             resource.md5,
                             'process'))
        conn.commit()

        cursor.close()
        conn.close()
        conn = None
    except MySQLdb.Error, e:
        print "DB Error %s" % e
    finally:
        if conn: conn.close()


def exists(url):
    retval = True
    conn = None
    try:
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='sharehp', charset='utf8')
        cursor = conn.cursor()
        sql = "SELECT id FROM sharehp_spide_resource WHERE md5 = '" + hashlib.md5(url).hexdigest() + "'"
        cursor.execute(sql)
        conn.commit()

        if int(cursor.rowcount) <=0:
            retval = False

        cursor.close()
        conn.close()
        conn = None
    except MySQLdb.Error, e:
        print "DB Error %s" % e
    finally:
        if conn: conn.close()
    return retval





