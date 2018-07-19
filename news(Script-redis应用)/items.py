# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy




class NewsItem(scrapy.Item):
    news_img_url = scrapy.Field()
    news_url = scrapy.Field()
    news_title = scrapy.Field()
    news_summay = scrapy.Field()
    linksid = scrapy.Field()


