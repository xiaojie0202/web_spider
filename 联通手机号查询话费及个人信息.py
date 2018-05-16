import requests
import time
import re
import json


class GetPhoneTariff(object):

    def __init__(self, phone, password):
        self.session = requests.Session()
        self.phone = phone
        self.password = password
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}

    def login_unicom(self):
        """
        自动登录中国联通
        :return: boolean， 登录成功返回True，登录失败返回False
        """
        login_headers = self.headers
        login_headers['Host'] = 'uac.10010.com'
        login_headers['Referer'] = 'http://uac.10010.com/portal/hallLogin'

        # 输入密码input框获取焦点的时候发送get请求， 会获取个cookie  ckuuid
        ckuuid_url = 'https://uac.10010.com/portal/Service/CheckNeedVerify?callback=jQuery17206328033706325524_1525102835951&userName=%s&pwdType=01&_=%s' % (
            self.phone, str(int(time.time())))
        self. session.get(url=ckuuid_url, headers=login_headers)
        # 此页面再次获取cookie  uacverifykey
        self.session.get(url='http://uac.10010.com/portal/Service/CreateImage?t=%s' %
                         str(int(time.time())), headers=login_headers)

        # 发送验证码 携带cookie   uacverifykey   ckuuid
        c_time = int(time.time())
        url = 'https://uac.10010.com/portal/Service/SendCkMSG?callback=jQuery17209749269944548633_1525103158591&req_time=%s&mobile=%s&_=%s' % (
            c_time, self.phone, c_time)
        self.session.get(url=url, headers=login_headers)
        # jQuery17209749269944548633_1525103158591({resultCode:"7096",redirectURL:"null",errDesc:"null",msg:'系统忙，请稍后再试。',needvode:"0",errorFrom:"null"});
        # 等待用户输入验证码
        verification = input('请输入验证码:')

        # 发送登录请求， 获取登录cookie
        c_time = int(time.time())
        login_url = 'https://uac.10010.com/portal/Service/MallLogin?callback=jQuery172013683158086553893_1525106413187&req_time=%s&redirectURL=http://www.10010.com&userName=%s&password=%s&pwdType=01&productType=01&redirectType=03&rememberMe=1&verifyCKCode=%s&_=%s' % (
            str(c_time), self.phone, self.password, verification, str(c_time))
        response = self.session.get(url=login_url, headers=login_headers)
        print(response.text)
        code = int(
            re.search(
                r'resultCode:"(?P<code>\d+)"',
                response.text).group('code'))
        if code != 0000:
            msg = re.search(r'msg:\'(?P<msg>.+)\'', response.text).group('msg')
            print('登录失败:%s' % msg)
            return False
        cookie_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        print(cookie_dict)
        print('登录成功')
        return True

    def init_query_cookie(self):
        """
        初始化 Cookies
        :return:
        """
        self.login_unicom()
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Host': 'iservice.10010.com',
            'Origin': 'http://iservice.10010.com',
            'Referer': 'http://iservice.10010.com/e4/index_server.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}

        # 处理一个叫e3的cookie
        self.session.post(url='http://iservice.10010.com/e3/static/query/searchPerInfo/?_=%s' %
                          str(int(time.time())), headers=self.headers)
        self.session.post(url='http://iservice.10010.com/e3/static/query/searchPerInfoUser/?_=%s' %
                          str(int(time.time())), headers=self.headers)
        self.session.get(url='http://iservice.10010.com/e3/static/query/message/pageList?_=%s&currentPage=1&pageSize=2' %
                         str(int(time.time())), headers=self.headers)
        self.session.post(url='http://iservice.10010.com/e3/static/check/checklogin/?_=%s' %
                          str(int(time.time())), headers=self.headers)
        self.save_cookies()

    def save_cookies(self):
        """
        保存cookies到数据库
        :return:
        """
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)

    def get_info(self):
        self.init_query_cookie()
        response = self.session.post(
            url='http://iservice.10010.com/e3/static/query/userinfoquery?_%s' % str(int(time.time())), headers=self.headers)
        return json.loads(response.text)


if __name__ == '__main__':
    a = GetPhoneTariff(phone=18526088455, password='020920')
    info_dict = a.get_info()
    print(info_dict)
    print('-' * 50)
