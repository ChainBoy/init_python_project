# -*- coding:utf-8 -*-


# @version: 1.0
# @author:
# @date: '14-4-10'


import os
import logging
import threading
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError, InterpolationMissingOptionError, Error

import simplejson as json

from utils.logger import Logger

_lock = threading.RLock()


class Environment():
    instance = None

    def __init__(self):
        self._working_path = ""
        self._app_name = ""

    @staticmethod
    def get_instance():
        if not Environment.instance:
            Environment.instance = Environment()
        return Environment.instance

    def init_by_file_name(self, start_file_path, start_file_name, start_file_depth=1):
        start_file_name = os.path.join(start_file_path, start_file_name)
        self.init(start_file_name, start_file_depth)

    def init(self, start_file_name, start_file_depth):
        """
        初始化应用环境
        :param start_file_name:   调用本方法的代码文件的完整路径
        :param start_file_depth:  调用本方法的代码文件距离工作目录的深度。如果在工作目录下，深度为1；如果在工作目录的一级子文件夹下，深度为2， 以此类推。
        """
        self._working_path, self._app_name = self._parse_start_file_name(
            start_file_name, start_file_depth)

        self._set_working_path(self._working_path)

        self._init_logger()

        self._configure_parser = ConfigParser()
        self._is_configure_loaded = False
        self._load_configure()

    def get_db_setting(self, db_setting_section_name):
        return self.get_configure_value(db_setting_section_name, "host"), \
            self.get_configure_value(db_setting_section_name, "db"), \
            self.get_configure_value(db_setting_section_name, "user"), \
            self.get_configure_value(db_setting_section_name, "passwd")

    def get_app_name(self):
        return self._app_name

    def get_working_path(self):
        return self._working_path

    def _get_configure_value(self, section, key):
        value = None
        try:
            value = self._configure_parser.get(section, key)
            return value
        except NoSectionError, e:
            logging.error(e.message)
            return None
        except InterpolationMissingOptionError, e:
            value = e.message.split("rawval : ")
            if value and len(value) > 1:
                value = value[1][:-1]
            else:
                raise Error
        return value

    def get_configure_value(self, section, key, default="", value_type=str):
        _lock.acquire()
        value = self._get_configure_value(section, key)
        _lock.release()
        if value_type in [str, unicode]:
            pass
        elif value_type in [int, long]:
            value = int(value)
        elif value_type in [float]:
            value = float(value)
        elif value_type == json:
            value = json.loads(value)
        else:
            pass
        value = default if value is None else value
        return value

    def set_configure_value(self, section, key, value=""):
        _lock.acquire()
        if not section in self._configure_parser.sections():
            self._configure_parser.add_section(section)
        if type(value) == dict:
            value = json.dumps(value)
        self._configure_parser.set(section, key, value)
        with file(self._config_path, "w") as fp:
            self._configure_parser.write(fp)
        _lock.release()

    def _parse_start_file_name(self, start_file_name, start_file_depth):
        """
        解析启动文件名称和该文件深度，返回程序工作目录和程序名称
        :param start_file_name:   调用本方法的代码文件的完整路径
        :param start_file_depth:  调用本方法的代码文件距离工作目录的深度。如果在工作目录下，深度为1；如果在工作目录的一级子文件夹下，深度为2， 以此类推。
        :return:
        """

        start_file_name = start_file_name.replace("\\", "/")
        file_name_parts = start_file_name.split('/')
        file_name_parts.remove("")
        if not file_name_parts:
            logging.error(u"启动文件输入参数错误，输入的不是完整的文件名: " + start_file_name)
            return

        app_name = file_name_parts[-1]
        if "." in app_name:
            app_name = app_name[:app_name.rindex(".")]
        file_name_parts = file_name_parts[:(start_file_depth) * -1]
        working_dir = os.sep.join(file_name_parts)
        return working_dir, app_name

    def _init_logger(self, logging_file_name="logging.conf"):
        log_file_whole_name = os.path.join(
            self._working_path, "conf", logging_file_name)
        print "Load logging file:", log_file_whole_name
        Logger.load_configure(log_file_whole_name)

    def _load_configure(self):
        configure_file_name = os.path.join(
            self._working_path, "conf", self._app_name + ".conf")
        print "Load configure file:", configure_file_name
        if self._is_configure_loaded:
            return
        if not configure_file_name:
            return
        self._configure_parser.read(configure_file_name)

    def _set_working_path(self, work_path):
        work_path = os.path.abspath(work_path)
        os.chdir(work_path)
        print "Set working dir:", work_path


if __name__ == "__main__":
    # Environment.get_instance()._load_configure()
    # print Environment.get_instance().get_configure_value("zhiShiTuPu",
    # "user")
    print Environment.get_instance()._parse_start_file_name(
        "F:\\newgit\\nluData\\query-crawler\\crawler\\query_crawler.py", 1)
