# coding=utf-8
import tornado.concurrent
import tornado.gen
from tornado.ioloop import IOLoop

from mycelery import celery_task
from tools.tool import check_tornado_future_status


@tornado.gen.coroutine
def do_longtime_task():
    """
    调用celery中task的函数

    假设我们有个超级耗时任务： do_longtime_task

    :return:
    """

    future = tornado.concurrent.Future()
    do_longtime_task = celery_task.celery_do_longtime_task.delay(1000 * 100000)
    check_tornado_future_status(do_longtime_task, future)
    yield future
    ret = future.result()
    raise tornado.gen.Return(ret)


@tornado.gen.coroutine
def main():
    ret = yield do_longtime_task()
    print "最终ret=%s" % ret


if __name__ == '__main__':
    ioloop = IOLoop.instance()
    ioloop.run_sync(main)
