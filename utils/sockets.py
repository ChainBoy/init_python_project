# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-12-08

import socket
from dnsproxy import socks
_default_timeout = 5
# socket.setdefaulttimeout(_default_timeout)

BASE_SOCKET = socket.socket


class Sockets(object):
    pass

    @staticmethod
    def check_host_port(host, port, timeout=_default_timeout):
        # socket.create_connection((host, port), timeout=5)
        try:
            port = int(port)
        except ValueError, TypeError:
            return -1
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((host, port))
        except socket.gaierror:
            # Name or service not known
            return -1
        except socket.timeout:
            # timed out
            return -1
        else:
            return -1
        finally:
            s.close()
        return 1

    @staticmethod
    def set_socket_proxy(host, port, socket_type=5):
        if socket_type == 4:
            socks.PROXY_TYPE_SOCKS4
        else:
            socks.PROXY_TYPE_SOCKS5
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, host, proxy)
        socket.socket = socks.socksocket

    @staticmethod
    def cancel_socket_proxy():
        socket.socket = BASE_SOCKET
        socket.socket.setproxy()
