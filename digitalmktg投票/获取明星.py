import requests
from bs4 import BeautifulSoup

# 先获取tocken

start_dict = {"hkMaleIdol": {'div_id': 'vote-list-hkmaleidol'},
              "hkFemaleIdol": {'div_id': 'vote-list-hkfemaleidol'},
              "hkGroupIdol": {'div_id': 'vote-list-hkgroupidol'},
              "asiaIdol": {'div_id': 'vote-list-asiaidol'}
              }
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1; EML-AL00 Build/HUAWEIEML-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.143 Crosswalk/24.53.595.0 XWEB/358 MMWEBSDK/23 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x2607023A) NetType/4G Language/zh_CN'
}
session = requests.Session()
response = session.get(url='https://yahoo.digitalmktg.com.hk/buzz2018/vote?lang=zh-CN', headers=headers)
session.cookies.update({'rxx': '2n4vuur1hag.1bm18h0k&v=1'})

soup = BeautifulSoup(response.text, 'lxml')

for key, value in start_dict.items():
    start_list = soup.find(name='div', id=value['div_id']).find_all(name='img', attrs={'class': 'voting-select'})
    for start_img in start_list:

        name = start_img.attrs.get('data-optiondesc')
        id = start_img.attrs.get('data-optionid')
        start_dict[key][name] = id
import json
print(json.dumps(start_dict))

