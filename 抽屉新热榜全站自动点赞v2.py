from concurrent.futures import ThreadPoolExecutor, wait
from bs4 import BeautifulSoup
import json
import requests
import time

class Chouti(object):
    '''
    抽屉新热榜全站自动点赞
    '''
    def __init__(self, phone, password):
        # 请求携带的认证信息
        self._login_post_date = {
            'phone': phone,
            'password': password,
            'oneMonth': 1}
        # 请求携带的headers
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36'
        }
        self.session = requests.Session()
        # 用于存放每条新闻的ID的队列
        # self.links_id = queue.Queue()
        self.proxies = {'https': 'https://101.236.60.225:8866'}

    def login_chouti(self):
        '''
        登陆抽屉，主要用于获取cookie
        :return:
        '''
        self.session.get(url='https://dig.chouti.com/', headers=self._headers, proxies=self.proxies)
        respones = self.session.post(url='https://dig.chouti.com/login', data=self._login_post_date, headers=self._headers, proxies=self.proxies)  # 请求登录cookie
        # {"result":{"code":"9999", "message":"", "data":{"complateReg":"0","destJid":"cdu_51313511426"}}}
        respones = json.loads(respones.text)
        if respones['result']['code'] == '9999':
            print('登陆抽屉成功')
            return True
        else:
            print('登陆抽屉失败: %s' % respones['result']['message'])
            return False

    def get_chouti_html(self, page):
        '''
        用于获取抽屉的分页
        :param page: 页数
        :return: 响应Rsponse对象
        '''
        respones = self.session.get(url='https://dig.chouti.com/all/hot/recent/%s' % page, headers=self._headers, proxies=self.proxies)
        return respones

    def handel_chouti_html(self, future):
        '''
        获取抽屉每个页面中所有新闻的ID
        :param future:
        :return:
        '''
        respones = future.result()
        future.links_id = []
        soup = BeautifulSoup(respones.text, 'lxml')
        news_div = soup.find(id='content-list')
        news_list = news_div.find_all('div', attrs={'class': 'item'})
        for i in news_list:
            news_id = i.find('i')
            future.links_id.append(news_id.text)

    def recommend(self, future):
        '''
        推荐
        :param future:
        :return:
        '''
        for i in future.links_id:
            text = self.session.post(url='https://dig.chouti.com/link/vote?linksId=%s' % i, headers=self._headers, proxies=self.proxies)
            print(text.text)

    def cancel_recommend(self, futrre):
        '''
        取消推荐
        :param futrre:
        :return:
        '''
        for i in futrre.links_id:
            text = self.session.post(url='https://dig.chouti.com/vote/cancel/vote.do', data={'linksId': i}, headers=self._headers, proxies=self.proxies)
            print(text.text)

    def start(self, option):
        '''
        多线程异步启动
        :param option:  True(推荐) or False(取消推荐)
        :return:
        '''
        self.login_chouti()
        pool = ThreadPoolExecutor(30)
        result = [pool.submit(self.get_chouti_html, i) for i in range(1, 121)]
        for i in result:
            i.add_done_callback(self.handel_chouti_html)
            i.add_done_callback(self.cancel_recommend if not option else self.recommend)

        wait(result)
        print('操作完毕')

    def low_start(self):
        '''
        单线程推荐
        :return:
        '''
        self.login_chouti()
        for index in range(1, 121):
            print('*'*20, '第%d页' % index, '*'*20)
            respones = self.session.get(url='https://dig.chouti.com/all/hot/recent/%s' % index, headers=self._headers, proxies=self.proxies)
            soup = BeautifulSoup(respones.text, 'lxml')
            news_div = soup.find(id='content-list')
            news_list = news_div.find_all('div', attrs={'class': 'item'})
            for i in news_list:
                news_id = i.find('i')
                text = self.session.post(url='https://dig.chouti.com/link/vote?linksId=%s' % news_id.text,
                                    headers=self._headers, proxies=self.proxies)
                print(text.text)


if __name__ == '__main__':

    start = time.time()
    c = Chouti(phone='*******', password='********')
    c.start(True)
    end = time.time()
    print('*' * 80)
    print(end-start)