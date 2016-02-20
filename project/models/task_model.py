# -*- coding:utf-8 -*-

# @version: 1.0
# @author: ZhangZhipeng
# @date: 2015-11-13


from ..utils.base_model import BaseModel


class TaskModel(BaseModel):
    line = None
    fields = []
    mark = None
    word_name = None
    start_time = None
    end_time = None
    search_by_hour = False
    search_by_province = False
    search_by_city = False

    # name 用于标识 唯一任务: word_name + "_" + str(line)
    name = None

    status = 0
    # STATUS_DEFAULT = 0
    # STATUS_HAS_GET = 1
    # STATUS_ALL_DOWNLOAD = 2
    # STATUS_ALL_UPLOAD = 3
    # search_done_status = False
    # download_done_status = False
    # thread_run_num = 0
    # thread_done_num = 0
