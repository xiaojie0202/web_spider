from bs4 import BeautifulSoup
import requests
import datetime
import time
import os


class KeXieSpider(object):
    """
    爬去www.hast.net.cn所有公告，增量爬去，每12小时一次
    """
    def __init__(self):
        self.new_date = datetime.datetime.now()
        self.code = 'utf-8'

    # 初始化爬去所有的公告
    def init_spider(self):
        for i in range(1, 37):
            url = 'http://www.hast.net.cn/general/index?cid=109&page={0}&per-page=15'.format(i)
            self.get_page_content(url)

    # 获取主要内容，和附件连接
    def get_article(self, url):
        response = requests.get(url=url)
        soup = BeautifulSoup(response.text, 'lxml')
        article = ''
        # 文章
        sarticle = soup.find(name='article', attrs={'class': 'show'}).find_all(name='p')
        for i in sarticle:
            article += i.text + os.linesep
            print(article)
        # accessory_link
        accessory = soup.find(name='div', attrs={'class': 'tabContent active', 'style': "height:auto"})
        accessory_link = ''
        if accessory:
            accessory_link = 'http://www.hast.net.cn%s' % accessory.find(name='a').attrs.get('href')
        return article, accessory_link

    # 提取每页的内容
    def get_page_content(self, url):
        response = requests.get(url=url)
        self.code = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'lxml')
        list_view = soup.find(name='div', attrs={'class': 'news-list'})
        news_list = list_view.find_all(name='div', recursive=False)
        self.get_info(news_list)
        self.new_date = datetime.datetime.strptime(news_list[0].find(name='span', attrs={'style': 'margin-right: 20px;'}).text, '%Y-%m-%d')

    # 提取每也需要的内容
    def get_info(self, soup):
        # 标题， 发布时间， 主要内容， 福建连接，摘要
        # title, release_time, content, accessory_link, abstract
        for i in soup:
            self.extract_info(i)

    # 提取每个页面的每条公告
    def extract_info(self, i):
        context = {}
        a = i.find(name='a', attrs={'class': 'item page-1'}).attrs.get('href')
        if a.find('general?id') != -1:
            url = 'http://www.hast.net.cn{0}'.format(a)
            # 主要内容 # 附件连接
            content, accessory_link = self.get_article(url)
            # 标题
            title = i.find(name='p', attrs={'class': 'news-list-title'}).find(name='b').text
            # 发布时间
            release_time = i.find(name='span', attrs={'style': 'margin-right: 20px;'}).text
            # 摘要
            abstract = i.find(name='p', attrs={'class': 'news-detail'}).text
            context['title'] = title
            context['release_time'] = release_time
            context['abstract'] = abstract.replace('\u3000', ' ')
            context['content'] = content
            context['accessory_link'] = accessory_link
            print(context)
            self.persistence(context)

    def increment_spider(self):
        url = 'http://www.hast.net.cn/general?cid=109'
        response = requests.get(url=url)
        soup = BeautifulSoup(response.text, 'lxml')
        list_view = soup.find(name='div', attrs={'class': 'news-list'})
        news_list = list_view.find_all(name='div', recursive=False)
        for i in news_list:
            release_time = i.find(name='span', attrs={'style': 'margin-right: 20px;'}).text
            if datetime.datetime.strptime(release_time, '%Y-%m-%d') > self.new_date:
                self.extract_info(i)
        self.new_date = datetime.datetime.strptime(news_list[0].find(name='span', attrs={'style': 'margin-right: 20px;'}).text, '%Y-%m-%d')

    # 数据持久化
    def persistence(self, content_dict):
        '''
        可以在此连接数据库，格式如下
        :param content_dict:{'title': '文章标题', 'release_time': '发布时间', 'abstract':'文章摘要', 'content': 文章内容， 'accessory_link'： 附件连接}
        :return:
        '''
        with open('date_info.txt', 'a+', encoding=self.code) as f:
            f.write(str(content_dict))
            f.write('\n')

    # 循环，每12小时增量爬取一次
    def start(self):
        self.init_spider()
        while True:
            time.sleep(43200)
            self.increment_spider()


if __name__ == '__main__':
    a = KeXieSpider()
    a.start()
