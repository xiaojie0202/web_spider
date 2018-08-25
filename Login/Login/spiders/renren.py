# -*- coding: utf-8 -*-
import scrapy
import execjs
from scrapy import Request
import json
import os


def get_js_data(password, public_key):
    js = open(os.path.join(os.path.dirname(__file__), 'renren_getrsapwd.js'), 'r')
    ctx = execjs.compile(js.read())
    data = dict(rsapwd=ctx.call('GetRSAPwd', password, public_key), uniqueTimestamp=ctx.call('GetDate'))
    return data


class RenrenSpider(scrapy.Spider):
    name = 'renren'
    allowed_domains = ['renren.com']
    start_urls = ['http://renren.com/']

    def start_requests(self):
        yield Request(method='GET', url='http://www.renren.com/SysHome.do', callback=self.handel_rk_login,
                      meta={'cookiejar': True})

    def handel_rk_login(self, response):
        # http://login.renren.com/ajax/getEncryptKey
        yield Request(method='GET', url='http://login.renren.com/ajax/getEncryptKey', meta={'cookiejar': True},
                      callback=self.login)

    def login(self, response):
        # {"isEncrypt":true,"e":"10001","n":"bc3fd6437b90227fc9895f10459187a81286ac40a7dcbf0ab59b9ba0212b5b61","maxdigits":"19","rkey":"9d6c98b7df8d1c66a353b1e7c93cc12e"}
        rkey = json.loads(response.text).get('rkey')
        public_key = json.loads(response.text).get('n')
        data = get_js_data('wangyaojie150300', public_key)
        print(response)
        yield Request(method='POST',
                      url='http://www.renren.com/ajaxLogin/login?1=1%s' % data['uniqueTimestamp'],
                      headers={'Content-Type': 'application/x-www-form-urlencoded',
                               'X-Requested-With': 'XMLHttpRequest', },
                      body='email=17612226296&icode=&origURL=http://www.renren.com/home&domain=renren.com&key_id=1&captcha_type=web_login&password={0}&rkey={1}&f=http://www.renren.com/home'.format(
                          data['rsapwd'], rkey),
                      meta={'cookiejar': True},
                      callback=self.get_homeurl)

    def get_homeurl(self, response):
        # {"code":true,"homeUrl":"http://www.renren.com/home"}
        print(response.text)
        yield Request(url=json.loads(response.text)['homeUrl'], meta={'cookiejar': True}, callback=self.parse)

    def parse(self, response):

        print(response.text)
