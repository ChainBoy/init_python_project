# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-12-01

# source: sqlmap/lib/core/option.py line_no: 1105
# https://github.com/sqlmapproject/sqlmap

import socket
from dns.resolver import Resolver
from dns.exception import DNSException


resolver = Resolver()

_dnscache = {}
dns_name_servers = [
    '114.114.114.114',
    '223.5.5.5',
    '223.6.6.6',
    '202.106.196.115',
    '8.8.8.8',
    '219.141.136.10',
]

resolver.nameservers = dns_name_servers + resolver.nameservers
print "dns servers:", resolver.nameservers


def start_dns_cache(file_name=None):
    load_hosts_dns_setting(file_name)
    set_socket_getaddrinfo(file_name)
    dump_hosts_dns_setting(file_name)


def load_hosts_dns_setting(file_name):
    if not file_name:
        return
    global _dnscache
    try:
        with file(file_name)as f:
            lines = f.read().splitlines()
            for i in lines:
                line = i.strip()
                ip_host = i.split(" ")
                if len(ip_host) != 2:
                    continue
                ip, host = ip_host
                addrinfo = (2, 1, 0, '', (ip, 80))
                _dnscache.setdefault((host, 80, 0, 1), [])
                _dnscache[(host, 80, 0, 1)].append(addrinfo)
    except:
        pass


def dump_hosts_dns_setting(file_name):
    if not file_name:
        return
    dns_list = set([])
    for hostinfo, addrinfo_list in _dnscache.items():
        host = hostinfo[0]
        for addrinfo in addrinfo_list:
            ip = addrinfo[-1][0]
            dns_list.add(ip + " " + host + "\n")
    with file(file_name, "w")as f:
        f.write("".join(dns_list))


def set_socket_getaddrinfo(file_name=None):
    def _getaddrinfo(*args, **kwargs):
        # print
        global _dnscache
        if args in _dnscache:
            # print args, " in cache", _dnscache[args]
            return _dnscache[args]
        else:
            _dnscache.setdefault(args, [])
            # print args, "not in cache"
            addrinfo_list = get_addrinfo(*args[:1])
            if not addrinfo_list:
                _dnscache[args] = socket._getaddrinfo(*args, **kwargs)
                return _dnscache[args]
            for i in addrinfo_list:
                addrinfo = (2, 1, 0, '', (i, args[1]))
                # print args, "add address:", addrinfo
                _dnscache[args].append(addrinfo)
            if file_name:
                with file(file_name, "a")as f:
                    dns_setting = i + " " + args[0] + "\n"
                    f.write(dns_setting)
            return _dnscache[args]

    if not hasattr(socket, '_getaddrinfo'):
        socket._getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = _getaddrinfo


def get_addrinfo(host):
    try:
        return [host.to_text() for host in resolver.query(host)]
    except DNSException, e:
        return []


def test():
    set_socket_getaddrinfo()
    import urllib
    import requests
    urllib.urlopen('http://baidu.com')
    requests.get("http://baidu.com")
    urllib.urlopen('http://10.20.12.10:26680/client/weibo')


def test_get_addr(hosts=None):
    if type(hosts) in (tuple, list):
        for i in hosts:
            if not i:
                continue
            # print i
            for addrinfo in get_addrinfo(i):
                print addrinfo, i


if __name__ == '__main__':
    test()
    hosts = """
    api.weibo.com
    beacon.sina.com.cn
    login.sina.com.cn
    login.weibo.cn
    passport.weibo.com
    rs.sinajs.cn
    s.weibo.com
    weibo.com
    www.weibo.com
    """
    hosts = hosts.replace(" ", "").splitlines()
    test_get_addr(hosts)
    start_dns_cache("test.dns.set")
