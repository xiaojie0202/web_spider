'''
需求分析:
1. 先抓取一页商品
2. 访问呢每个商品， 抓取商品所属店铺的 商品数量以及以拼数量， 满足用户指定的商品数量以及以拼数量则继续
3. 进入店铺查看当前店铺正拼的单子有几单 (拼单人数)  满足条件则提取店铺链接

所需条件：
1. 店铺商品数量
2. 店铺所有拼单数量

3. 拼单人数
'''
import requests
import json
import re


class PDDFilter(object):

    def __init__(self, good_num, mall_sales, indent_count, page_count):
        """
        :param good_num: 店铺商品数量
        :param mall_sales: 店铺销量
        :param indent_count : 当前拼单数量
        """
        self.headers = {
            'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
        }
        self.good_num = good_num
        self.mall_sales = mall_sales
        self.indent_count = indent_count
        self.page_count = page_count
        self.data = []
        # {"error_code":40001,"error_msg":""}

    # 根据关键字搜索商品
    def get_goods(self, gjz):
        """
        获取指定关键字的商品
        :param gjz: String 关键字
        :param page_count:  int 需要获取多少也
        :return:
        """
        headers = {
            'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
        }
        for page in range(1, self.page_count + 1):
            url = 'http://apiv3.yangkeduo.com/search?q=%s' % gjz
            response = requests.get(url=url, headers=self.headers)
            # 所有商品的列表
            good_list = json.loads(response.text)

            # IP受到限制
            if self.is_ip(good_list):
                continue

            # 开始获取商品
            for good in good_list.get('items'):
                # 店铺ID
                if not good.get('ad', None):
                    continue
                print(json.dumps(good))
                mall_id = good['ad']["mall_id"]
                # 获取店铺信息
                response = requests.get(url='https://api.pinduoduo.com/mall/%s/info' % mall_id, headers=self.headers)
                mall_info = json.loads(response.text)

                # IP受到限制
                if self.is_ip(mall_info):
                    continue

                # 店铺商品数量
                good_num = mall_info['goods_num']
                if good_num < self.good_num:
                    continue
                # 店铺销售量
                mall_sales = mall_info['mall_sales']
                if mall_sales < self.mall_sales:
                    continue
                # 获取店铺的当前拼单数量
                response = requests.post(url='https://api.pinduoduo.com/api/leibniz/mall/groups', json={"mall_id": mall_id}, headers=self.headers)
                pdd_data = json.loads(response.text)
                # IP受到限制
                if self.is_ip(mall_info):
                    continue
                # 店铺当前拼单数量
                pdd_count = len(pdd_data['result'])
                if pdd_count >= self.indent_count:
                    self.data.append('https://mobile.yangkeduo.com/mall_page.html?mall_id=%s' % mall_id)



    # 判断IP是否受到限制
    def is_ip(self, data):
        if data.get('error_code', None):
            if data['error_code'] == 40001:
                return True
        else:
            return False


if __name__ == '__main__':
    headers = {
        'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
    }
    response = requests.get(url='http://mobile.yangkeduo.com/goods.html?goods_id=%s' % 2864060639, headers=headers)
    json_find = re.findall('window.rawData=\s+(?P<n>{.+});', response.text)
    print(json_find[0])
