# -*- coding:utf-8 -*-


# @version: 1.0
# @author: Zhipeng Zhang
# @date: '2015/5/15'

import os

from utils.environment import Environment

DATABASE_CONF_SECTION = "database"


class Configure(object):
    __instance = None

    def __init__(self, environment=None):
        "environment is instance. 实例后的对象."
        self.__environment = environment

    @staticmethod
    def get_instance(environment=None):
        if not Configure.__instance:
            Configure.__instance = Configure(environment)
        return Configure.__instance

    @property
    def database(self):
        host, db, user, passwd = self.__environment.get_db_setting(DATABASE_CONF_SECTION)
        return {"host": host or "127.0.0.1", "db": db or "baike", "user": user or "root", "passwd": passwd or ""}

    # write you code in here.

    def _get_value(self, section, key, default="", value_type=str):
        value = self.__environment.get_configure_value(section, key)
        if value_type in [str, unicode]:
            pass
        elif value_type in [int, long]:
            value = int(value)
        elif value_type in [float]:
            value = float(value)
        else:
            pass
        value = default if value is None else value
        return value


    def _set_value(self, section, key, value=""):
        self.__environment.set_configure_value(section, key, value)

if __name__ == "__main__":
    pass
