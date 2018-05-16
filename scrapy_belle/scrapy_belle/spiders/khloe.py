# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import Request
from scrapy import Selector
from .. import items
from .. import models
session = models.DBSession()
from scrapy.http.response.html import HtmlResponse

class KhloeSpider(scrapy.Spider):
    name = 'khloe'
    allowed_domains = ['kendall-jenner.net', 'meghan-markle.net', 'jenna-dewan.com', 'nathaliekelley.us', 'sarah-hyland.org', 'jaimekingfan.net']
    start_urls = ['http://kendall-jenner.net/gallery/thumbnails.php?album=topn',
                  'http://meghan-markle.net/gallery/thumbnails.php?album=topn',
                  'http://jenna-dewan.com/photos/thumbnails.php?album=topn&cat=0',
                  'http://nathaliekelley.us/photos/thumbnails.php?album=topn&cat=0',
                  'http://sarah-hyland.org/photos/thumbnails.php?album=topn&cat=0',
                  'http://jaimekingfan.net/gallery/thumbnails.php?album=topn&cat=0',
                  ]

    def parse(self, response):
        index_url = re.search(r'http://.+/.+/', response.url).group()
        img_a_list = Selector(response=response).xpath('//table[@class="maintable "]/tr//a[@href]/@href').extract()
        for i in img_a_list:
            url = index_url + i
            if i.startswith('thumbnails'):
                yield Request(method='GET', url=url, callback=self.parse)
            elif i.startswith('displayimage'):
                pid = re.search(r'pid=\d+', i).group()
                print(pid)
                img_url = '%sdisplayimage.php?%s&fullsize=1' % (index_url, pid)
                yield Request(url=img_url, callback=self.show_img_page, method='GET')

    def show_img_page(self, response):
        this_url = response.url
        index_url = re.search(r'http://.+/.+/', this_url).group()
        domain_name = this_url.split('/')[2]
        image_urls = Selector(response=response).xpath('//img/@src').extract_first()
        path = image_urls.replace('%20', ' ')
        path = domain_name + '/' + path
        url = index_url + image_urls
        yield items.ImagesItem(image_url=[url], path=path)
