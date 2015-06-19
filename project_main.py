# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-06-18

import os
import sys
import logging

from utils.environment import Environment
from configure.configure import Configure
from project.project import Project

reload(sys)

sys.setdefaultencoding('utf-8')


class ProjectMain(object):
    """doc for Main"""
    def __init__(self, config_path=""):
        super(ProjectMain, self).__init__()

        environment = Environment.get_instance()
        environment.init_by_file_name("/.", os.path.basename(os.getcwd()), 1)
        configure = Configure.get_instance(environment)
        self._project = Project()

    def start(self):
        logging.info("%s Started." % __name__)
        self._project.start()
        logging.info("%s Closed." % __name__)

if __name__ == '__main__':
    project_main = ProjectMain()
    project_main.start()
