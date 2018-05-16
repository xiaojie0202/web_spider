# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from crop_info import models


class CnhubSpiderPipeline(object):
    def process_item(self, item, spider):
        item_name = item.__class__.__name__
        if item_name == 'CategoryOne':  # 如果是一级分类
            a = models.CategoryOne.objects.create(**item)
            print('创建一级菜单：%s' % a)
        elif item_name == 'CategoryTwo':
            cate_one = models.CategoryOne.objects.get(name=item['cate_one'])
            a = models.CategoryTwo.objects.create(name=item['name'], category_one=cate_one)
            print('创建二级菜单：%s' % a)
        elif item_name == 'CategoryThree':
            cate_two = models.CategoryTwo.objects.get(name=item['cate_two'])
            a = models.CategoryThree.objects.create(category_tow=cate_two, name=item['name'])
            print('创建三级菜单:%s' % a)
        elif item_name == 'Commodity':
            category_three = models.CategoryThree.objects.get(name=item.get('category_three'))
            crop = models.Commodity.objects.create(category_three=category_three,
                                                   name=item.get('name'),
                                                   price=item.get('price'),
                                                   unit=item.get('unit'),
                                                   place_of_dispatch=item.get('place_of_dispatch'),
                                                   start_wholesale=item.get('start_wholesale'),)

            for i in item.get('specification'):
                a = models.Specification.objects.filter(**i)
                if a:
                    crop.specification.add(*a)
                else:
                    crop.specification.create(**i)

            print('创建商品 %s' % crop)

