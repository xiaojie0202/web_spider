from bs4 import BeautifulSoup
import requests
import re


# 判断是否登陆登陆装饰器
def is_login(func):
    def werrp(self, *args, **kwargs):
        if self.is_login[0]:
            return func(self, *args, **kwargs)
        else:
            return '登陆失败%s' % self.is_login[1]
    return werrp


class GitHub(object):

    def __init__(self, username, password):
        '''
        :param username:  GitHub 账号
        :param password:  GitHub 密码
        '''
        self.username = username
        self.password = password
        self.authenticity_token = None
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Host':'github.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Referer': 'https://github.com',
            'Origin': 'https://github.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.1.3228.1 Safari/537.36'
        }
        # 保存所有cookies
        self.cookies = {}
        # 请求登陆session
        self.is_login = self.login_github()

    def login_github(self):
        '''
        登陆GitHub，
        :return: 成功则返回(True, response), 否则返回(False, 错误信息)
        '''
        response = requests.get(url='https://github.com/login')
        self.cookies.update(response.cookies.get_dict())
        soup = BeautifulSoup(response.text, 'lxml')
        authenticity_token = soup.find(name='input', attrs={'name': 'authenticity_token'}).attrs['value']
        response = requests.post(url='https://github.com/session',
                                 data={'commit': 'Sign in', 'utf8': '✓',
                                       'authenticity_token': authenticity_token,
                                       'login': self.username, 'password': self.password},
                                 headers=self.headers,
                                 cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        erro_div = soup.find(name='div', attrs={'class': 'flash flash-full flash-error'})
        if not erro_div:
            self.cookies.update(response.cookies.get_dict())
            print('登陆成功')
            return True, response
        else:
            erro = erro_div.find(name='div', attrs={'class': 'container'}).text
            return False, erro

    @is_login
    def recent_login_info(self):
        '''
        获取最近登陆信息[{'地址':'家里', 'IP':'1.1.1.1', '登陆时间':''}]
        # https://github.com/settings/security # 最近登陆信息  地址IP
        :return:
        '''
        info = []
        response = requests.get(url='https://github.com/settings/security', headers=self.headers, cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        info_div_list = soup.find_all(name='div', attrs={'class': 'Box-row p-3 js-user-session session-device '})
        for info_div in info_div_list:
            address_div = info_div.find(name='strong', attrs={'class': 'd-block'})
            address = address_div.get_text().strip()

            time = info_div.find(name='time').text

            info.append({'登陆地址': address.split('\n')[0], '登陆IP': address.split('\n')[1].strip(), '登陆时间': time})
        return info

    def _parse_repositories(self, response, dict):
        '''
        :param response: requests请求响应对象
        :param dict:  将解析好的数据存到到dict字典中
        '''
        soup = BeautifulSoup(response.text, 'lxml')
        repositories_a = soup.find_all(name='a',attrs={'class': 'd-flex flex-items-baseline flex-items-center f5 mb-2'})
        for i in repositories_a:
            # 拼接项目地址
            href = 'https://github.com%s' % i.attrs['href']

            # 解析出来项目名称
            name = re.search(r'https://github.com/.+/(?P<name>.+)', href).group('name')

            # data-ga-click="Dashboard, click, Repo list item click - context:user visibility:public fork:true"
            is_fork = re.search(r'fork:(?P<fork>true|false)', i.attrs['data-ga-click']).group('fork')

            # 判断是否是fork并更新到字典中
            if is_fork == 'true':
                dict['fork'].update({name: href})
            else:
                dict['self'].update({name: href})

        pass

    @is_login
    def get_repositories(self):
        '''
        获取个人全部代码仓库{'self':{'项目名称':'项目地址'}, 'fork':{'仓库名称','仓库地址'}}
        url = 'https://github.com/dashboard/ajax_repositories?button=&utf8=✓&repos_cursor=Nw=='
        :return:
        '''
        repositories = {'self': {}, 'fork': {}}
        self._parse_repositories(self.is_login[1], repositories)
        headers = self.headers
        headers.update({'x-requested-with':'XMLHttpRequest'})
        response = requests.get(url='https://github.com/dashboard/ajax_repositories?button=&utf8=✓&repos_cursor=Nw==', headers=headers, cookies=self.cookies)
        self._parse_repositories(response, repositories)
        return repositories

    @is_login
    def get_user_info(self):
        '''
        获取个人信息:{'个人信息':{'名字':'','邮箱':''},仓库:{}, 最近登陆信息:[]}
        url = ''
        :return:
        '''
        soup = BeautifulSoup(self.is_login[1].text, 'lxml')
        username = soup.find(name='meta', attrs={'name': 'user-login'}).attrs['content']
        response = requests.get(url='https://github.com/%s' % username, headers=self.headers, cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        email = soup.find(name='a', attrs={'class': 'u-email'}).text
        name = soup.find(name='span', attrs={'itemprop': 'name'}).text
        return {'个人信息': {'name': name, 'username': username, 'email': email}, '仓库': self.get_repositories(), '最近登陆信息': self.recent_login_info()}

if __name__ == '__main__':
    a = GitHub(username='用户名', password='密码')
    print(a.get_user_info())