# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-06-18

import logging


class Project(object):
    """docstring for Project"""
    def __init__(self):
        super(Project, self).__init__()

    def start(self):
        logging.info("project run ..")
