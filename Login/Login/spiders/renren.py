# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json


class RenrenSpider(scrapy.Spider):
    name = 'renren'
    allowed_domains = ['renren.com']
    start_urls = ['http://renren.com/']

    def start_requests(self):
        yield Request(method='GET', url='http://www.renren.com/SysHome.do', callback=self.handel_rk_login,
                      meta={'cookiejar': True})

    def handel_rk_login(self, response):
        # http://login.renren.com/ajax/getEncryptKey
        yield Request(method='GET', url='http://login.renren.com/ajax/getEncryptKey', meta={'cookiejar': True}, callback=self.login)
        # {"isEncrypt":true,"e":"10001","n":"bc3fd6437b90227fc9895f10459187a81286ac40a7dcbf0ab59b9ba0212b5b61","maxdigits":"19","rkey":"9d6c98b7df8d1c66a353b1e7c93cc12e"}

    def login(self, response):
        rkey = json.loads(response.text).get('rkey')
        # uniqueTimestamp2015年，9月，星期三，0点，21秒，961毫秒
        print(rkey)
        yield Request(method='POST',
                      url='http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=2018611029128',
                      body='email=17612226296&icode=&origURL=http://www.renren.com/home&domain=renren.com&key_id=1&captcha_type=web_login&password=wangyaojie150300&rkey={0}&f='.format(rkey),
                      meta={'cookiejar': True},
                      callback=self.parse)

    def parse(self, response):
        print(response.text)
