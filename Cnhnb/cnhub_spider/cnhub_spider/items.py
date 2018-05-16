# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CnhubSpiderItem(scrapy.Item):
    category_one = scrapy.Field()
    categroy_two = scrapy.Field()
    category_three = scrapy.Field()
    url = scrapy.Field()


# 一级分类
class CategoryOne(scrapy.Item):
    name = scrapy.Field()


# 二级分类
class CategoryTwo(scrapy.Item):
    cate_one = scrapy.Field()
    name = scrapy.Field()


# 三级分类
class CategoryThree(scrapy.Item):
    cate_two = scrapy.Field()
    name = scrapy.Field()


# 商品
class Commodity(scrapy.Item):
    category_three = scrapy.Field()  # 所属三级菜单
    name = scrapy.Field()  # 商品名称
    price = scrapy.Field()  # 价格
    unit = scrapy.Field()  # 单位
    place_of_dispatch = scrapy.Field()  # 发货地
    start_wholesale = scrapy.Field()  # 起批数量
    specification = scrapy.Field()  # 规格



'''
# 一级分类
class CategoryOne(scrapy.Item):
    name = scrapy.Field()


# 二级分类
class CategoryTwo(scrapy.Item):
    category_one = models.ForeignKey(CategoryOne, verbose_name='所属一级分类')
    name = scrapy.Field()


# 三级分类
class CategoryThree(scrapy.Item):
    category_tow = models.ForeignKey(CategoryTwo, verbose_name='所属二级分类')
    name = scrapy.Field()


# 商品
class Commodity(scrapy.Item):
    category_three = models.ForeignKey(CategoryThree, verbose_name='所属三级分类')
    name = models.CharField(max_length=128, verbose_name='商品名称')
    start_wholesale = models.CharField(max_length=64, verbose_name='起批数量')
    specification = models.ManyToManyField('Specification')


# 规格
class Specification(scrapy.Item):
    name = models.CharField(max_length=64, verbose_name='规格名称')
    value = models.CharField(max_length=64, verbose_name='规格值')
{'一级菜单':'苹果', '二级菜单':'热带水果','三级菜单':'芒果', '商品':{'name':'相乘芒果','起批数量':'100'} ,'规格':{品种：‘hello’}}

'''