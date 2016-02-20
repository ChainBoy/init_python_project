# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-06-24
import time
import socket
import httplib
import requests

from urllib2 import Request

socket.setdefaulttimeout(20)


class Downloader(object):

    """docstring for Downloader"""

    def __init__(self):
        pass

    @staticmethod
    def get(url, params=None, decode="utf-8", try_num=5, wait_time=1, timeout=20, *args, **kwargs):
        content = ""
        while try_num:
            try:
                response = requests.get(
                    url, params=(params or {}), timeout=timeout, *args, **kwargs)
                if response.status_code >= 400:
                    raise BaseException
                content = response.content
                if decode:
                    content = content.decode(decode)
                return content
            except BaseException:
                time.sleep(wait_time)
                try_num -= 1
                continue
        return content

    @staticmethod
    def get_status_by_httplib(url, try_num=5, wait_time=1, default_code=404):
        while try_num:
            try:
                request = Request(url)
                host = request.get_host()
                selector = request.get_selector()
                conn = httplib.HTTPConnection(host)
                conn.request("GET", selector)
                res = conn.getresponse()
                return res.status
                # return True if res.status < 400 else False
            except Exception, e:
                # raise e
                try_num -= 1
                time.sleep(wait_time)
                continue
        return default_code


if __name__ == '__main__':
    print Downloader.get("http://www.baidu.com/").encode("utf8")
    raw_input("press key to continue.")
