from scrapy.contrib.throttle import AutoThrottle
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
from . import models

class MyDupeFilter(object):

    def __init__(self, session):
        self.url_set = set()
        self.session = session

    @classmethod
    def from_settings(cls, settings):
        session = models.DBSession()
        return cls(session)

    def request_seen(self, request):

        if self.session.query(models.RequestUel).filter(models.RequestUel.url == request.url).count():
            return True
        self.session.add(models.RequestUel(url=request.url))
        self.session.commit()
        return False

    def open(self):
        pass

    def close(self, reason):
        self.session.close()

    def log(self, request, spider):

        pass








