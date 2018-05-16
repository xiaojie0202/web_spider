from scrapy import signals
from crop_info import models


class MyExtensions:

    def __init__(self, crawler):
        self.crawler = crawler
        self.noisy = False
        self.crawler.signals.connect(self.stop_engine, signals.engine_stopped)


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def stop_engine(self):
        # print('引擎结束的时候执行此函数')
        models.RequestUrl.objects.all().delete()
