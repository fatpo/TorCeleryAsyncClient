# TorCeleryAsyncClient
基于tornado + celery 的一个异步客户端 

# 背景
基于tornado开发，如果想利用好epool，那么就尽可能要用到异步，像比较常用的服务都有异步客户端：
```
mysql: https://github.com/snower/TorMySQL
redis: https://github.com/thefab/tornadis
抓取网页:  http_client = tornado.httpclient.AsyncHTTPClient()
```

但是我们总会遇到一些情况，需要自己写一个异步客户端：
```
比如获取一个第三方服务商融云token，我们调用它的api，但是它的api只支持同步调用。
比如有一个超级耗时操作，需要执行10多秒后才能返回它的value。
```
本项目利用celery能异步处理数据并返回的特性，先在celery中定义好一个镜像处理task，记为A，那么这个A()是真正处理逻辑的地方，然后我们再在tornado项目中写了一个调用A()的task，记为B，B中定义了个future，如果A()处理完毕，B()的celery_task.ready()为True，我们会在future中设置好result。然后我们利用tornado的call_later()，实际上是利用tornado的timeout，在每一次epoll醒来的时候检查一下B()中future的状态，如果future的状态被set_result，那么我们就认为这个B()处理完毕，获取future的result返回即可，具体逻辑可以看以下的#核心代码。

# 环境
```
celery==4.1.0
redis==2.10.6
tornado==5.0
```

# 核心代码
```
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

```

# 使用示例
第一步，在celery中建立好处理task：
```
@app.task(name="mycelery.celery_task.celery_do_longtime_task")
def celery_do_longtime_task(some_param):
    """
    这里是真正处理task的地方！
    
    这里我们模拟一个耗时操作，然后返回一个value

    :param some_param:  某些参数，这里模拟一个大数据如 999999999
    :return: 某一个值
    """
    ret = 1
    for i in range(some_param):
        ret += 1
    print "ret=%s" % ret
    return ret

```
第二步，在我们客户端建立调用方法：
```
@tornado.gen.coroutine
def do_longtime_task():
    """
    目的：调用celery中 celery_do_longtime_task()
    :return:
    """

    future = tornado.concurrent.Future()
    do_longtime_task = celery_task.celery_do_longtime_task.delay(1000 * 100000)
    check_tornado_future_status(do_longtime_task, future)
    yield future
    ret = future.result()
    raise tornado.gen.Return(ret)
```
第三步，在tornao中调用第二步中的调用方法：
```
@tornado.gen.coroutine
def main():
    ret = yield do_longtime_task()
    print "最终ret=%s" % ret

if __name__ == '__main__':
    ioloop = IOLoop.instance()
    ioloop.run_sync(main)
```

