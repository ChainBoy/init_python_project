# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-11-03

from re import findall
from os import listdir
import os.path
os.path.listdir = listdir
del listdir

from bloom_filter import BloomFilter

from configure.configure import FILE_MEMORY_BUFFER_TYPE as MEMORY_BUFFER_TYPE
from configure.configure import FILE_MEMORY_BUFFER_SIZE as MEMORY_BUFFER_SIZE
from configure.configure import FILE_MEMORY_BUFFER_LENGTH as MEMORY_BUFFER_LENGTH
from configure.configure import FILE_CUT_FILE_SIZE as CUT_FILE_SIZE
from configure.configure import FILE_SPLIT_CHAR as SPLIT_CHAR
from configure.configure import FILE_BASE_SAVE_FILE_PATH as BASE_SAVE_FILE_PATH

from configure.configure import DEBUG
from configure.configure import MemoryBufferType


MEMORY_BUFFER_SIZE = 1024L * 1000 * MEMORY_BUFFER_SIZE


class FileSaver(object):
    FilE_SAVERS = {}

    def __init__(self, task_model):
        self._task_model = task_model
        # print task_model.word_name

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
        self._file_path = self._init_dir()
        self._file_name = ""
        self._build_file_name()
        self._set_history_size()
        print "FileSaver file_name", self._file_name

    # def __new__(cls, word_name, start_time, end_time):
    #     file_saver = FileSaver.FilE_SAVERS.get(word_name, FileSaver(word_name, start_time, end_time))
    #     FileSaver.FilE_SAVERS[word_name] = file_saver
    #     return file_saver

    def get_word_id(self):
        return self._task_model.line

    def add(self, detail):
        self._buffer.append(self._join_detail(detail))
        if self._check_memory_buffer_has_out():
            log = "%s memory buffer has out. %.2f MB, dump to file." % (
                detail.url, self._buffer_size / 1024.0 / 1000)
            self._save_log(log)
            self._dump_data_to_file()

    def close(self):
        self._dump_data_to_file()
        self._save_file_name_to_history(end=True)

    def _join_detail(self, detail):
        save_list = []
        for key in self._task_model.fields:
            try:
                save_list.append(getattr(detail, key))
            except AttributeError:
                logging.error("not find key:%s in detail, set ''." % key)
                save_list.append("")
        # save_list = [detail.url, detail.time, detail.source,
                # detail.zan_num, detail.zhuan_num, detail.ping_num,
                # detail.content]
        line = SPLIT_CHAR.join(save_list)
        self._buffer_length += 1

        self._buffer_size += len(line)
        self._history_size += len(line)
        return line

    def commit(self):
        pass

    def _init_dir(self):
        file_path = os.path.join("{base}", "{task}", "{s_time}_{e_time}", "")
        file_path = file_path.format(base=BASE_SAVE_FILE_PATH, task=self._task_model.word_name,
                                     s_time=self._task_model.start_time, e_time=self._task_model.end_time).decode("utf8")
        return file_path

    def _build_file_name(self):
        file_path = self._file_path
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        template_file_name = "%s%s-%s.dat" % (file_path,
                                              self._task_model.word_name.decode("utf8"), "%s")
        template_file_index_regexp = "%s-%s.dat" % (
            self._task_model.word_name.decode("utf8"), "(\d{0,})")
        template_file_name_regexp = "%s-%s.dat" % (
            self._task_model.word_name.decode("utf8"), "\d{0,}")

        history_files = "\n".join([i for i in os.path.listdir(file_path)])
        # print "history_files: \n", history_files
        self._history_files = [
            file_path + i for i in findall(template_file_name_regexp, history_files)]
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
                self._file_name = file_name
                return file_name
            self._file_name = file_name
            return file_name

    def _set_history_size(self):
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
            self._save_file_name_to_history()
            if DEBUG:
                self._save_log("file: %s has big." %
                               self._file_name.encode('utf8'))

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
        self._build_file_name()

    def _save_file_name_to_history(self, end=False):
        # 保存历史文件名的文件
        file_name = self._file_path + "history.files"
        end_all_mark = "ALL"
        files_status = {}
        status_ok = "True"
        status_no = "False"
        for i in self._history_files:
            files_status[i.encode("utf8")] = status_no

        if os.path.exists(file_name):
            # 将历史的记录历史文件中的状态加载，去重.
            with file(file_name) as f:
                for i in f.readlines():
                    line = i.strip()
                    if not line:
                        break
                    try:
                        k_file_name, v_upload_status = line.split("\t")
                    except:
                        k_file_name, v_upload_status = line, status_no
                    files_status[
                        k_file_name] = status_ok if v_upload_status == status_ok else status_no
            # 添加至记录历史文件中
            files_status[self._file_name.encode("utf8")] = status_no

        for i in files_status:
            with file(file_name, "a")as f:
                f.write(i + "\t" + status_no + "\n")
        if end:
            # 如果已经结束，则在结尾标记全部下载完成.
            with file(file_name, "a")as f:
                f.write(end_all_mark + "\t" + status_no + "\n")

    def _save_log(self, string):
        if DEBUG:
            with file("save.log", "a")as f:
                print string
                f.write(string + "\n")
