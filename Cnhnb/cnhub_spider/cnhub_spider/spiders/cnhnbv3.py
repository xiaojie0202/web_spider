# -*- coding: utf-8 -*-
import scrapy



class Cnhnbv3Spider(scrapy.Spider):
    name = 'cnhnbv3'
    allowed_domains = ['www.cnhnb.com']
    start_urls = ['http://www.cnhnb.com/p/zzzm/']

    def parse(self, response):
        pass
