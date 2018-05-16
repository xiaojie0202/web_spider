# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
from scrapy.http import Request
from .. import items

class CnhubSpider(scrapy.Spider):
    name = 'cnhub'
    allowed_domains = ['www.cnhnb.com']
    start_urls = ['http://www.cnhnb.com/']

    def parse(self, response):
        # 一级菜单
        cate_one = Selector(response=response).xpath('//dl[@data-target]')
        cate_one_list = []
        for cate in cate_one:
            cate_one_text = cate.xpath('.//a/text()').extract_first()
            cate_one_list.append(cate_one_text)
            yield items.CategoryOne(name=cate_one_text) # yield 一级菜单

        # 二三级菜单
        cate_two_three = Selector(response=response).xpath('//div[@data-index]')
        for index, cate in enumerate(cate_two_three):
            menue = cate.xpath('.//div[@class="sub-cate"]/dl')
            for two_three_cate in menue:  # 二级菜单
                two_cate = two_three_cate.xpath('.//dt//a/text()').extract_first()
                yield items.CategoryTwo(cate_one=cate_one_list[index], name=two_cate)  # yield 二级菜单
                three_cate_path = two_three_cate.xpath('.//dd//h3')
                for three_cate in three_cate_path:  # 三级菜单
                    title = three_cate.xpath('.//a/text()').extract_first()
                    link = three_cate.xpath('.//a/@href').extract_first()
                    yield items.CategoryThree(cate_two=two_cate, name=title)  # yield 三级菜单
                    yield Request(url=link, method='get', callback=self.get_crop_page)


    # 访问三级分类页面的所有页码
    def get_crop_page(self, response):
        # 解析出来当前页面商品的连接
        crop_link_list = Selector(response=response).xpath('//div[@id="imgList"]//li')
        for crop_link in crop_link_list:
            crop_link = crop_link.xpath('.//a/@href').extract_first()
            yield Request(method='get', url=crop_link, callback=self.spider_crop_info)
        # 解析出来当前页的所有页码
        three_page = Selector(response=response).xpath('//div[@class="page mt_30  mb_20"]//a/@href').extract()
        for link_a in three_page:

            yield Request(method='get', url=link_a, callback=self.get_crop_page)


    # 处理商品信息
    def spider_crop_info(self, response):
        specification = []
        cate_three = Selector(response=response).xpath('//div[@class="container"]/div[@class="position"]/a[2]/text()').extract_first()  # 三级菜单
        crop_name = Selector(response=response).xpath('//div[@class="tit clearfix"]/h1/text()').extract_first()  # 商品名称
        place_of_dispatch = Selector(response=response).xpath('//div[@class="txt clearfix"]/span/text()').extract_first()  # 发货地
        price = float(Selector(response=response).xpath('//div[@class="price clearfix"]//span[@class="red fs24 mr5"]/text()').extract_first().strip())  # 价格
        unit = Selector(response=response).xpath('//div[@class="price clearfix"]//span[3]/text()').extract_first()  #单位unit
        start_wholesale = Selector(response=response).xpath('//div[@class="price clearfix"]//span[4]/text()').extract_first()  #起批start_wholesale

        specification_span = Selector(response=response).xpath('//div[@class="breed clearfix"]/span[@class="align-1"]') #规格specification
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




