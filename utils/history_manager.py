# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-11-13

from re import findall
from os import listdir
import os.path
os.path.listdir = listdir
del listdir

from bloom_filter import BloomFilter
from configure.configure import BASE_SAVE_FILE_PATH
from configure.configure import DEBUG

from configure.configure import HIS_MEMORY_BUFFER_TYPE as MEMORY_BUFFER_TYPE
from configure.configure import HIS_MEMORY_BUFFER_SIZE as MEMORY_BUFFER_SIZE
from configure.configure import HIS_MEMORY_BUFFER_LENGTH as MEMORY_BUFFER_LENGTH
from configure.configure import HIS_CUT_FILE_SIZE as CUT_FILE_SIZE
from configure.configure import MemoryBufferType


MEMORY_BUFFER_SIZE = 1024L * 1000 * MEMORY_BUFFER_SIZE


class HistoryManager(object):
    BLOOM_FILTERS = {}
    FilE_SAVERS = {}

    def __init__(self, task_model):
        self._bloom_filter = HistoryManager.BLOOM_FILTERS.get(
            task_model.name, BloomFilter())
        print "HistoryManager get bloom filter ", self._bloom_filter
        HistoryManager.BLOOM_FILTERS[task_model.name] = self._bloom_filter
        self._task_model = task_model

        # 缓存数据
        self._buffer = []
        # 缓存数据大小
        self._buffer_size = 0L
        # 缓存数据条数
        self._buffer_length = 0L
        # 标记当前分片文件大小
        self._history_size = 0L

        # 标记最大分片文件字节数
        self._cut_file_size = 1024L * 1000 * CUT_FILE_SIZE
        # 当前分片文件序号
        self._file_index = 0
        # 任务历史分片文件
        self._history_files = []
        # 当前文件名字
        self._file_name = self._build_file_name()
        self._load_history_to_bloom_filter()
        print "HistoryManager file_name", self._file_name

    def check_url_has_download(self, url):
        if not self._bloom_filter.exists(url):
            log = "%s add into bloom filter." % url
            self._save_log(log)
            return False
        else:
            # log = "%s has in bloom filter." % detail.url
            # self._save_log(log)
            return True

    def add_url_to_history(self, url):
        # bloom_filter.exists 会自动添加, 所以注释掉bloom_filter.add
        # self._bloom_filter.add(url)
        self._buffer.append(url)
        self._update_buffer(url)
        if self._check_memory_buffer_has_out():
            log = "%s memory buffer has out. %.2f MB, dump to file." % (
                url, self._buffer_size / 1024.0 / 1000)
            self._save_log(log)
            self._dump_data_to_file()

    def close(self):
        self._dump_data_to_file()

    def _update_buffer(self, line):
        self._buffer_length += 1

        self._buffer_size += len(line)
        self._history_size += len(line)
        return line

    def _build_file_name(self):
        file_path = os.path.join("{base}", "{task}", "{s_time}_{e_time}", "")
        file_path = file_path.format(base=BASE_SAVE_FILE_PATH, task=self._task_model.word_name,
                                     s_time=self._task_model.start_time, e_time=self._task_model.end_time).decode("utf8")
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        template_file_name = "%s%s-%s.history" % (
            file_path, self._task_model.word_name.decode("utf8"), "%s")
        template_file_index_regexp = "%s-%s.history" % (
            self._task_model.word_name.decode("utf8"), "(\d{0,})")
        template_file_name_regexp = "%s-%s.history" % (
            self._task_model.word_name.decode("utf8"), "\d{0,}")

        history_files = "\n".join([i for i in os.path.listdir(file_path)])
        # print "history_files: \n", history_files
        self._history_files = [
            file_path + i for i in findall(template_file_name_regexp, history_files)]
        if DEBUG:
            print "self._history_files: \n", "\n".join(self._history_files)
        max_index = max(
            [int(i) for i in findall(template_file_index_regexp, history_files)] + [0])
        self._file_index = max_index
        while True:
            file_name = template_file_name % self._file_index
            if os.path.exists(file_name):
                if os.path.getsize(file_name) >= self._cut_file_size:
                    self._file_index += 1
                    continue
                return file_name
            return file_name

    def _load_history_to_bloom_filter(self):
        "把历史下载添加至过滤器"
        def __load_file_to_bloom_filter(file_name, bloom_filter):
            "把一个文件的记录添加至过滤器"
            with file(file_name)as f:
                print u"load file:%s to bloom filter." % file_name
                while True:
                    line = f.readline()
                    if not line:
                        break
                    try:
                        url = line.strip()
                        # print "bloom add url:%s-----" % url
                        bloom_filter.add(url)
                    except Exception, e:
                        # 没有记录日志的必要.
                        raise e

        # 所有的历史文件添加至布隆过滤器
        for file_name in self._history_files:
            __load_file_to_bloom_filter(file_name, self._bloom_filter)

        if not os.path.exists(self._file_name):
            return
        self._history_size = os.path.getsize(self._file_name)

    def _check_memory_buffer_has_out(self):
        if MEMORY_BUFFER_TYPE == MemoryBufferType.size:
            if self._buffer_size >= MEMORY_BUFFER_SIZE:
                return True
        elif MEMORY_BUFFER_TYPE == MemoryBufferType.length:
            if self._buffer_length >= MEMORY_BUFFER_LENGTH:
                return True
        else:
            pass

    def _dump_data_to_file(self):
        if self._check_file_has_out():
            self._build_file_name()
            self._history_size = 0L

        content = "\n".join(self._buffer) + "\n"
        with file(self._file_name, "a")as f:
            f.write(content.encode("utf8"))
        self._reset_init()

    def _check_file_has_out(self):
        # if os.path.getsize(self._file_name) >= self._cut_file_size:
        if self._history_size >= self._cut_file_size:
            return True

    def _reset_init(self):
        self._buffer = []
        self._buffer_size = 0L
        self._buffer_length = 0L
        self._file_name = self._build_file_name()

    def _save_log(self, string):
        if DEBUG:
            with file("history.log", "a")as f:
                print string
                f.write(string.encode("utf8") + "\n")
