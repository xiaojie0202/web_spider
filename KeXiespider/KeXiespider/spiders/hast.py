# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy import Request
from ..items import KexiespiderItem

class HastSpider(scrapy.Spider):
    name = 'hast'
    allowed_domains = ['hast.net.cn']
    start_urls = ['http://www.hast.net.cn/general?cid=109']

    def parse(self, response):
        page_link = Selector(response).xpath('//ul[@class="pagination"]/li')
        for page in page_link:
            page_href = page.xpath('./a/@href').extract_first()
            if page_href:
                page_url = 'http://www.hast.net.cn%s' %page_href
                yield Request(url=page_url, callback=self.parse)
        notice_list = Selector(response).xpath('//div[@id="w0"]/div[@class="news-list"]/div')
        for notice in notice_list:
            notice_a_href = notice.xpath('./a[@class="item page-1"]/@href').extract_first()
            if notice_a_href.find('general?id') != -1:
                notice_url = 'http://www.hast.net.cn%s' % notice_a_href
                yield Request(url=notice_url, callback=self.handle_notice)

    def handle_notice(self, response):
        # {'title': '文章标题', 'release_time': '发布时间', 'abstract':'文章摘要', 'content': 文章内容， 'accessory_link'： 附件连接}
        title = Selector(response).xpath('//article[@class="show"]/h2/text()').extract_first().strip()
        release_time = Selector(response).xpath('//time/text()').extract_first().strip().split('：')[1]
        abstract = Selector(response).xpath('//article[@class="show"]/p/text()').extract_first()
        content = '\n'.join(Selector(response).xpath('//article[@class="show"]/p/text()').extract())
        accessory_link = 'http://www.hast.net.cn%s' % Selector(response).xpath('//div[@class="tabContent active"]//a/@href').extract_first()
        yield KexiespiderItem(title=title, release_time=release_time, abstract=abstract, content=content, accessory_link=accessory_link)


