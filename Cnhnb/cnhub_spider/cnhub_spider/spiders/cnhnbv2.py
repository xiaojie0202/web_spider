# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.http import Request
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from .. import items
from crop_info import models





class Cnhnbv2Spider(scrapy.Spider):
    name = 'cnhnbv2'
    allowed_domains = ['www.cnhnb.com']
    start_urls = ['http://www.cnhnb.com/p/zzzm/']

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path='E:\code\chromedriver.exe')
        # self.browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')
        super(Cnhnbv2Spider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):  # 信号触发函数
        print('爬虫结束 停止爬虫')
        self.browser.quit()

    def parse(self, response):

        cate_div_list = Selector(response=response).xpath('//div[@id="cate2_div"]/div')
        for cate_div in cate_div_list:
            cate_two = cate_div.xpath('./a[@class="tit"]/text()').extract_first()
            yield items.CategoryTwo(cate_one='种子种苗', name=cate_two) # yield 二级菜单
            cate_three = cate_div.xpath('./p/a/text()').extract()
            for i in cate_three:
                yield items.CategoryThree(cate_two=cate_two, name=i)

        link_p_list = Selector(response=response).xpath('//div[@id="cate2_div"]//a/@href').extract()
        for a in link_p_list:
            if a == 'javascript:;':
                pass
            else:
                yield Request(url=a, callback=self.getpage_shangpin)

    def getpage_shangpin(self, response):
        page_list = Selector(response=response).xpath('//div[@class="page mt_30  mb_20"]//a/@href').extract()
        for page_a in page_list:
            if page_a == 'javascript:void(0);':
                pass
            else:
                yield Request(url=page_a, callback=self.getpage_shangpin)

        comm_li_list = Selector(response=response).xpath('//ul[@class="img-list clearfix"]//li/a[@class="text"]/@href').extract()
        for comm_a in comm_li_list:
            a = models.TempRequestUrl.objects.create(url=comm_a)
            print(a)
            # yield Request(url=comm_a, callback=self.handle_shangpin)

    def handle_shangpin(self, response):
        specification = []
        cate_three = Selector(response=response).xpath('//div[@class="container"]/div[@class="position"]/a[2]/text()').extract_first()  # 三级菜单
        crop_name = Selector(response=response).xpath('//div[@class="tit clearfix"]/h1/text()').extract_first()  # 商品名称
        place_of_dispatch = Selector(response=response).xpath('//div[@class="txt clearfix"]/span/text()').extract_first()  # 发货地
        price = float(Selector(response=response).xpath('//div[@class="price clearfix"]//span[@class="red fs24 mr5"]/text()').extract_first().strip())  # 价格
        unit = Selector(response=response).xpath('//div[@class="price clearfix"]//span[3]/text()').extract_first()  # 单位unit
        start_wholesale = Selector(response=response).xpath('//div[@class="price clearfix"]//span[4]/text()').extract_first()  # 起批start_wholesale

        specification_span = Selector(response=response).xpath('//div[@class="breed clearfix"]/span[@class="align-1"]')  # 规格specification
        for i in specification_span:
            value = i.xpath('./text()').extract_first()
            key = i.xpath('./label/text()').extract_first()
            specification.append({'name': key, 'value': value})

        yield items.Commodity(category_three=cate_three,
                              name=crop_name,
                              price=price,
                              place_of_dispatch=place_of_dispatch,
                              unit=unit,
                              start_wholesale=start_wholesale,
                              specification=specification)



