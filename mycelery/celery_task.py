# coding=utf-8
import sys

from celery import Celery, platforms

sys.path.append('..')

from mycelery import celery_config

platforms.C_FORCE_ROOT = True  # linux 下要root用户才不报错
app = Celery()
app.config_from_object(celery_config)


# task定义
@app.task(name="mycelery.celery_task.celery_do_longtime_task")
def celery_do_longtime_task(some_param):
    """
    这里我们模拟一个耗时操作，然后返回一个value

    :param some_param:  某些参数，这里模拟一个大数据如 999999999
    :return: 某一个值
    """
    ret = 1
    for i in range(some_param):
        ret += 1
    print "ret=%s" % ret
    return ret
