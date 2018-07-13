# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KexiespiderItem(scrapy.Item):
    # {'title': '文章标题', 'release_time': '发布时间', 'abstract':'文章摘要', 'content': 文章内容， 'accessory_link'： 附件连接}
    # name = scrapy.Field()
    title = scrapy.Field()
    release_time = scrapy.Field()
    abstract = scrapy.Field()
    content = scrapy.Field()
    accessory_link = scrapy.Field()