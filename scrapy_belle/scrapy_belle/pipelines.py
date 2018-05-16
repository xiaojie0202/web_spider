# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class KadaishanPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item.get(self.images_urls_field, []):
            yield Request(image_url, meta={'path': item.get('path')})

    def file_path(self, request, response=None, info=None):
        path = request.meta['path']
        return path
