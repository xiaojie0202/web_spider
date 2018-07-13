# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class KexiespiderPipeline(object):
    def open_spider(self, spider):
        self.f = open('data_info.txt', 'a+', encoding='utf-8')

    def process_item(self, item, spider):
        self.f.write(str(item))
        print(item)
        return item

    def close_spider(self, spider):
        self.f.close()