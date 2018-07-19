# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.web.client import Agent, getPage, ResponseDone, PotentialDataLoss
from twisted.internet import defer, reactor, protocol
from twisted.web._newclient import Response
from io import BytesIO
from news.items import NewsItem
from scrapy.utils.project import get_project_settings
import os

settings = get_project_settings()

class _ResponseReader(protocol.Protocol):

    def __init__(self, finished, txresponse, file_name):
        self._finished = finished
        self._txresponse = txresponse
        self._bytes_received = 0
        self.f = open(file_name, mode='wb')

    def dataReceived(self, bodyBytes):
        self._bytes_received += len(bodyBytes)

        # 一点一点的下载
        self.f.write(bodyBytes)

        self.f.flush()

    def connectionLost(self, reason):
        if self._finished.called:
            return
        if reason.check(ResponseDone):
            # 下载完成
            self._finished.callback((self._txresponse, 'success'))
        elif reason.check(PotentialDataLoss):
            # 下载部分
            self._finished.callback((self._txresponse, 'partial'))
        else:
            # 下载异常
            self._finished.errback(reason)

        self.f.close()


class NewsPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'chouti' and isinstance(item, NewsItem):
            agent = Agent(reactor)
            d = agent.request(
                method=b'GET',
                uri=bytes(item['news_img_url'], encoding='ascii')
            )
            file_name = os.path.join(settings.get('BASE_DIRS'), 'news_img/%s.jpg' % item['linksid'])
            d.addCallback(self._cb_bodyready, file_name=file_name)
            item['news_img_url'] = '%s.jpg' % item['linksid']
            return item
        return item

    def _cb_bodyready(self, txresponse, file_name):
        d = defer.Deferred()
        d.addBoth(self.download_result)
        txresponse.deliverBody(_ResponseReader(d, txresponse, file_name))
        return d

    def download_result(self, response):
        pass