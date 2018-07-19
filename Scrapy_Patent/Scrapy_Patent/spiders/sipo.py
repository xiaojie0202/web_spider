# -*- coding: utf-8 -*-
import scrapy


class SipoSpider(scrapy.Spider):
    name = 'sipo'
    allowed_domains = ['sipo.gov.cn']
    start_urls = ['http://epub.sipo.gov.cn/ ']

    def parse(self, response):
        pass
