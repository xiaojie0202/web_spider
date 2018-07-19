# -*- coding: utf-8 -*-
import scrapy


class TencentMicroblogSpider(scrapy.Spider):
    name = 'tencent_microblog'
    allowed_domains = ['qq.com']
    start_urls = ['http://qq.com/']

    def parse(self, response):
        pass
