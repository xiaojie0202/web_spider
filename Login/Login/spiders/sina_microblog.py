# -*- coding: utf-8 -*-
import scrapy


class SinaMicroblogSpider(scrapy.Spider):
    name = 'sina_microblog'
    allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com/']

    def parse(self, response):
        pass
