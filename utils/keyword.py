#!/bin/python
# -*- coding: utf-8 -*-


import jieba.analyse


class Keyword(object):

    def __init__(self):
        super(Keyword, self).__init__()

    def keyword(self, content):
        keywords = jieba.analyse.extract_tags(content, topK=10)
        return keywords


if __name__ == '__main__':
    pass
