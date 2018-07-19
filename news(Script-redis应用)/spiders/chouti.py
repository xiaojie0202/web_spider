# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy import Request
from scrapy.selector import Selector
from ..items import NewsItem


from scrapy_redis.spiders import RedisSpider


class ChoutiSpider(RedisSpider):
# class ChoutiSpider(scrapy.Spider):
    name = 'chouti'
    allowed_domains = ['chouti.com']
    # start_urls = ['https://dig.chouti.com/']
    redis_key = 'chouti:start_url'

    def make_requests_from_url(self, url):
        return Request(url=url, meta={'cookiejar': True}, dont_filter=True)

    def parse(self, response):
        print(response)
        yield Request(
            url='http://dig.chouti.com/login',
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            body='phone=8613121758648&password=woshiniba&oneMonth=1',
            callback=self.parse_check_login,
            meta={'cookiejar': True}
        )

    def parse_check_login(self, response):
        yield Request(
            url='https://dig.chouti.com/',
            callback=self.handel_page,
            meta={'cookiejar': True}
        )

    def handel_page(self, response):
        content_list = Selector(response=response).xpath('//div[@id="content-list"]/div[@class="item"]')
        for content in content_list:
            news_img_url = content.xpath('.//div[@class="part2"]/@share-pic').extract_first()
            news_url = content.xpath('.//div[@class="part1"]/a/@href').extract_first()
            news_title = content.xpath('.//div[@class="part2"]/@share-title').extract_first()
            news_summary = content.xpath('.//div[@class="part2"]/@share-summary').extract_first()
            news_linkid = content.xpath('.//div[@class="part2"]/@share-linkid').extract_first()
            yield NewsItem(news_img_url=news_img_url, news_url=news_url, news_title=news_title,
                           news_summay=news_summary, linksid=news_linkid)
            yield Request(url='https://dig.chouti.com/link/vote?linksId=%s' % news_linkid, method='POST',
                          meta={'cookiejar': True}, callback=self.recommend)
        # 解析页码
        page_list = Selector(response).xpath('//div[@id="dig_lcpage"]/ul/li')
        for page in page_list:
            page_url = 'https://dig.chouti.com%s' % page.xpath('./a/@href').extract_first()
            yield Request(url=page_url, callback=self.handel_page, meta={'cookiejar': True})

    def recommend(self, response):
        print(response.text)
