# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy import Request
from scrapy.http.cookies import CookieJar
from http.cookiejar import Cookie


class SipoSpider(scrapy.Spider):
    name = 'sipo'
    allowed_domains = ['sipo.gov.cn']
    start_urls = ['http://epub.sipo.gov.cn']

    def parse(self, response):
        body =  "showType=1&strSources=pip&strWhere=PA,IN,AGC,AGT,PR,DPR,IAN,MC,IA,IP+='%*%' or PAA,TI,ABH+='*'&numSortMethod=4&strLicenseCode=&numIp=0&numIpc=0&numIg=0&numIgc=0&numIgd=&numUg=0&numUgc=0&numUgd=&numDg=0&numDgc=0&pageSize=10&pageNow=1"
        yield Request(url='http://epub.sipo.gov.cn/patentoutline.action',
                      method='POST',
                      body=body,
                      callback=self.indo)

    def indo(self, response):
        print(response)
        print(response.text)
