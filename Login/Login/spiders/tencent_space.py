# -*- coding: utf-8 -*-
import scrapy


class TencentSpaceSpider(scrapy.Spider):
    name = 'tencent_space'
    allowed_domains = ['qq.com']
    start_urls = ['http://qq.com/']

    def parse(self, response):
        pass
