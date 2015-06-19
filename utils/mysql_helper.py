# -*- coding: utf8 -*-
# @author: 'zhangzhipeng'
# @date: '2015-04-10'

import logging

import mysql.connector as connor


connor.connect()


class MysqlHelper(object):
    """host="localhost", db="", user="root", passwd="", port=3306, pool_sizer=30, pool_name="mysql", commit_size=1"""
    commit_count = 0

    def __init__(self, *args, **kwargs):
        commit_size = kwargs.get("commit_size", -1)
        if commit_size > -1:
            self._commit_size = commit_size
            del kwargs["commit_size"]
        else:
            self._commit_size = 1
        self._last_row_id = None
        self._conn = connor.connect(*args, **kwargs)

    def insert(self, sql, params=None):
        cursor = self._create_cursor()
        try:
            cursor.execute(sql, params)
        except Exception, e:
            try:
                logging.error("Mysql Call error. SQL = %s, params = %s, Error.msg=%s" % (sql, str(params).encode("utf8"), e))
            except:
                print sql, params, e
        self._last_row_id = cursor.lastrowid
        self._commit()
        return cursor.rowcount

    def update(self, sql, params=None):
        return self.insert(sql, params)

    def delete(self, sql, params=None):
        return self.insert(sql, params)

    def select(self, sql, params=None):
        cursor = self._create_cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

    def commit(self):
        try:
            self._conn.commit()
        except connor.Error, msg:
            logging.error("Mysql commit error. message:%s." % msg)

    @property
    def last_row_id(self):
        return self._last_row_id

    def _create_cursor(self):
        # cursor = conn.cursor(cursor_class=conner.cursor.MySQLCursorDict)
        cursor = self._conn.cursor(dictionary=True)
        return cursor

    def _commit(self):
        self.__class__.commit_count += 1
        if self.__class__.commit_count == self._commit_size:
            self.commit()
            self.__class__.commit_count = 0

    def __del__(self):
        print "mysql close ..."
        self.commit()
        self._conn.close()


if __name__ == "__main__":
    mysql_helper = MysqlHelper(host="localhost", db="zentao", user="root", passwd="kaimen", port=3306, pool_size=2,
                               pool_name="mysql", commit_size=2)
    print 1, mysql_helper.select("show tables;")
    print 2, mysql_helper.select("show tables;")
    print 3, mysql_helper.select("show tables;")
    print 4, mysql_helper.select("show tables;")
    print 5, mysql_helper.select("select * from task;")
