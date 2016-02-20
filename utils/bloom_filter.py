#!/usr/bin/python
# coding=utf-8

"""根据布隆过滤器的数学模型，设置错误概率是0.001(0.1%)
求出所需的bitvector大小和所需要的hash函数的个数n，
再使用素数筛法求出从5开始的n个素数用来作为哈希的种子。
哈希函数，使用的是bkdrhash算法
"""

import pybloom

ERROR_RADIO = 0.001


class BloomFilter(pybloom.BloomFilter):

    def __init__(self, capacity=1000000, error_rate=ERROR_RADIO):
        pybloom.BloomFilter.__init__(self, capacity, error_rate=error_rate)
        self._set_fun()

    def _set_fun(self):
        self.has_value = self.add
        self.get = self.add
        self.exists = self.add

        self.insert = self.add
        self.set = self.add

def test_1():
    bloom_filter = BloomFilter()

    def _fun(fun, value):
        if fun == "get":
            print fun, value, bloom_filter.get(value)
        elif fun == "set":
            print fun, value
            bloom_filter.set(value)
        else:
            print "ERROR", fun, value

    print '---'
    _fun("get", "zhipeng")
    _fun("get", ["zhipeng"])
    _fun("get", {"name": "zhipeng"})

    print '---'
    _fun("set", "zhipeng")
    _fun("set", ["zhipeng"])
    _fun("set", {"name": "zhipeng"})

    print '---'
    _fun("get", "zhipeng")
    _fun("get", ["zhipeng"])
    _fun("get", {"name": "zhipeng"})

    print '---'
    _fun("set", "zhipeng")
    # with file("dump.bf", "w")as f:
    #     bloom_filter.tofile(f)


def test_2():
    bloom_filter_A = BloomFilter()
    bloom_filter_B = BloomFilter()
    bloom_filter_A.set("3687812060623025")
    bloom_filter_B.set(3687812060623025)
    import sys
    print "Memory for '3687812060623025'", sys.getsizeof(bloom_filter_A)
    print "Memory for 3687812060623025", sys.getsizeof(bloom_filter_B)
    # MyBloomFilter --> all result is 36.
    # BloomFilter --> all result is 32.


if __name__ == '__main__':
    test_1()
    test_2()
