
import requests
import string
from bs4 import BeautifulSoup

# 先获取tocken

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1; EML-AL00 Build/HUAWEIEML-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.143 Crosswalk/24.53.595.0 XWEB/358 MMWEBSDK/23 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x2607023A) NetType/4G Language/zh_CN'
}
session = requests.Session()
response = session.get(url='https://yahoo.digitalmktg.com.hk/buzz2018/vote?lang=zh-CN', headers=headers)
soup = BeautifulSoup(response.text, 'lxml')
tocken = soup.find(name='input', attrs={'name': 'token'}).attrs.get('value')
print(tocken)
print(session.cookies)
import random
response = session.get(url='https://yahoo.digitalmktg.com.hk/buzz2018/vote/captcha?lang=zh-CN&v=%s' % str(random.random()), headers=headers)
with open('1.png', 'wb') as f:
    f.write(response.content)
code = input('验证码:')

headers['X-CSRF-Token'] = tocken
headers['Content-Type'] = 'application/json;charset=UTF-8'
headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
headers['X-Requested-With'] = 'XMLHttpRequest'
headers['Host'] = 'yahoo.digitalmktg.com.hk'
headers['Origin'] = 'https://yahoo.digitalmktg.com.hk'
headers['Referer'] = 'https://yahoo.digitalmktg.com.hk/buzz2018/vote?lang=zh-CN'

data = {"hkMaleIdol": "23",
        "hkFemaleIdol": "59",
        "hkGroupIdol": "67",
        "asiaIdol": "79",
        "tncFlag": "Y",
        "email": '%s@%s.%s' % (''.join(random.sample(string.ascii_letters + string.digits, 10)), ''.join(random.sample(string.ascii_lowercase, 2)), 'com'),
        "captcha": code.strip(),
        "token": tocken.strip(),
        "deviceRef": str(random.randint(1111111111, 9999999999))
        }
response = session.post(url='https://yahoo.digitalmktg.com.hk/buzz2018/vote-api?lang=zh-CN', headers=headers, json=data)
#  {"code":-3,"message":"Captcha input is incorrect."} 验证码错误

print(response.text)

