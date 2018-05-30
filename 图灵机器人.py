#coding=utf-8
from urllib import parse, request
import json


class Turing_hadel(object):
    '''
    图灵机器人
    初始化传入文本信息，调用gettext获取图灵机器人思考后的文字
    '''
    def __init__(self,info, key):
        self.url = 'http://www.tuling123.com/openapi/api'
        self.key = key
        self.info = info
        self.userid = 'xiaojie'

    def getText(self):

        textmod = {
            'key': self.key,
            'info': self.info,
            'userid': self.userid,
        }

        # json串数据使用
        textmod = json.dumps(textmod).encode(encoding='utf-8')

        header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/json"}
        req = request.Request(url=self.url, data=textmod, headers=header_dict)
        res = request.urlopen(req)
        res = res.read()

        return res.decode(encoding='utf-8')
