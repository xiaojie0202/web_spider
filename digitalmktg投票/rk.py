import requests
from hashlib import md5
import json


# 若快
class RClient(object):
    """
    若快识别验证码
    """

    def __init__(self, username, password):
        self.username = username
        self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = '116179'
        self.soft_key = '5a46d7b6409c41fa8f28803e85fef87a'
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type=7110, timeout=60):
        """
        识别图片
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        while True:
            r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
            if r.status_code == 200:
                print(r.text)
                if r.text.find('Error') == -1:
                    return json.loads(r.text)

    def query_user(self):
        # http://api.ruokuai.com/info.json
        data = {
            'username': self.username,
            'password': self.password
        }
        r = requests.post(url='http://api.ruokuai.com/info.json', data=data, headers=self.headers)
        print(r.text)
        if r.text.find('Error') == -1:
            return True
        else:
            return False


if __name__ == '__main__':
    a = RClient(username='songxtan', password='an337918123')
    a.query_user()
    with open('1.png', 'rb') as f:
        b = a.rk_create(im=f.read())
        print(b)
