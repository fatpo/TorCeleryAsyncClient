# coding=utf-8
import tornado.ioloop


def check_tornado_future_status(celery_task, future):
    """
    celery状态检查辅助函数...
    Check the status of the celery task and set the result in the future
    """
    if not celery_task.ready():
        tornado.ioloop.IOLoop.current().call_later(
            0.1,  # 100ms
            check_tornado_future_status,
            celery_task,
            future)
    else:
        future.set_result(celery_task.result)
