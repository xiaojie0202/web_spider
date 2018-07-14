#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
爬取淘宝网页的，销量根标题
"""
from selenium import webdriver
from bs4 import BeautifulSoup

option = webdriver.ChromeOptions()
driver = webdriver.Chrome('F://chromedriver', chrome_options=option)

driver.get("https://s.taobao.com/search?q=%E7%88%AC%E8%99%AB%E4%BB%A3%E5%86%99&sort=sale-desc")

response = driver.page_source

soup = BeautifulSoup(response, 'lxml')
div_list = soup.find_all(name='div', attrs={'data-category': "auctions"})
for i in div_list:
    volume = i.find(name='div', attrs={'class': 'deal-cnt'}).text
    title = i.find(name='div', attrs={'class': 'row row-2 title'}).find(name='a').decode_contents().strip().replace('<span class="baoyou-intitle icon-service-free"></span>','').replace('<span class="H">', '').replace('</span>', '').strip()
    print([volume, title])
