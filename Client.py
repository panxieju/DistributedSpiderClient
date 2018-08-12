import queue
import random
import threading
import time
from functools import partial

import grpc
import multiprocessing

import message_pb2_grpc
from Spiders.Spider58 import Spider58
from Spiders.SpiderAnjuke import SpiderAnjuke
from Spiders.SpiderFang import SpiderFang
from Spiders.SpiderGanji import SpiderGanji
from Util.Utils import Utils
from message_pb2 import Request

spiders = ["Spider58", "SpiderAnjuke", "SpiderGanji", "SpiderFang"]


class Client(object):
    interval = 30
    status = dict()

    def __init__(self):
        for spider in spiders:
            self.status[spider] = True

    def requestUrl(self, spider):
        # 定义一个数据通道
        channel = grpc.insecure_channel('39.108.51.140:16305')
        # 定义一条管道
        stub = message_pb2_grpc.SpiderServerStub(channel)
        # 获取服务器返回的数据
        response = stub.req(Request(host=Utils.getIp(), timestamp=Utils.getTime(), spider=spider))
        if response.url is not None and response.url != '':
            pool = multiprocessing.Pool(1)
            # 注意了，向pool的map传递多个参数时，要使用partial,第二个参数以后的每个参数都要包含进来，一一对应好
            result = pool.map(partial(self.runSpider, url=response.url), (spider,))
            if not result[0]:
                self.status[spider] = False
                print("%s is blocked by firewall!")
                self.status[spider] = pool.map(self.waitFireWallExpire, (60 * 60,))[0]

    # 当遇到防火墙的时候，等待一个小时
    def waitFireWallExpire(self, seconds):
        time.sleep(seconds)
        return True

    def runSpider(self, spider, url):
        houseSpider = None
        if spider == 'Spider58':
            houseSpider = Spider58()
        if spider == 'SpiderAnjuke':
            houseSpider = SpiderAnjuke()
        if spider == 'SpiderGanji':
            houseSpider = SpiderGanji()
        if spider == 'SpiderFang':
            houseSpider = SpiderFang()
        if houseSpider is not None:
            return houseSpider.parseHouse(url)

    def crawl(self):
        while True:
            for spider in spiders:
                print("Running Spider> %s"%spider);
                if self.status[spider]:
                    threading.Thread(target=self.requestUrl, args=(spider,)).start()
                time.sleep(1)
            time.sleep(self.interval)


if __name__ == '__main__':
    client = Client()
    client.crawl()
