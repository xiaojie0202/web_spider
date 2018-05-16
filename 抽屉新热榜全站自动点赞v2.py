import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait


class Chouti(object):

    def __init__(self, phone, password):

        self._login_post_date = {
            'phone': phone,
            'password': password,
            'oneMonth': 1}
        self._headers = {
            'Origin': 'http://dig.chouti.com',
            'Referer': 'http://dig.chouti.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36'
        }
        self.session = requests.Session()

    def login_chouti(self):
        self.session.get(url='http://dig.chouti.com/', headers=self._headers)
        respones = self.session.post(url='http://dig.chouti.com/login', data=self._login_post_date, headers=self._headers, )  # 请求登录cookie
        print(respones.text)

    def get_chouti_html(self, page):
        respones = self.session.get(url='http://dig.chouti.com/all/hot/recent/%s' % page, headers=self._headers)
        return respones

    def handel_chouti_html(self, future):
        respones = future.result()
        future.links_id = []
        soup = BeautifulSoup(respones.text, 'lxml')
        news_div = soup.find(id='content-list')
        news_list = news_div.find_all('div', attrs={'class': 'item'})
        for i in news_list:
            news_id = i.find('i')
            future.links_id.append(news_id.text)

    def recommend(self, future):
        for i in future.links_id:
            text = self.session.post(url='http://dig.chouti.com/link/vote?linksId=%s' % i, headers=self._headers)
            print(text.text)

    def cancel_recommend(self, futrre):
        for i in futrre.links_id:
            text = self.session.post(url='http://dig.chouti.com/vote/cancel/vote.do', data={'linksId': i}, headers=self._headers)
            print(text.text)

    # 终极版本，使用Session 管理cookie
    def start_v2(self):
        self.login_chouti()
        pool = ThreadPoolExecutor(60)
        result = [pool.submit(self.get_chouti_html, i) for i in range(1, 121)]
        for i in result:
            i.add_done_callback(self.handel_chouti_html)
            i.add_done_callback(self.recommend)

        wait(result)
        print('操作完毕')


if __name__ == '__main__':
    c = Chouti(phone='86手机号', password='登录密码')
    c.start_v2()
