# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-12-08

from ...utils.base_model import BaseModel


class ProxyType(BaseModel):
    http = "http"
    https = "https"
    socket = "socket"


class ProxyEntity(BaseModel):
    proxy = None

    type = ProxyType.http
    host = None
    port = 80

    def set_proxy(self, proxy):
        self.proxy = proxy
        itype, address = proxy.split("://")
        port = 80
        if itype.lower() == "https":
            port = 443
        elif itype.lower() == "http":
            port = 80
        else:
            # socket ?
            pass

        host, port = address.split(":")
        try:
            port = int(port)
        except Exception:
            pass

        self.type = itype
        self.host = host
        self.port = port
