from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait
import requests
import os
import openpyxl
import xlrd
import threading
import configparser
import sys

requests.packages.urllib3.disable_warnings()


class Spider(object):

    def __init__(self, verification_file, filter, api_key):
        # 保存结果的xlsx文件
        self.save_file = 'save.xlsx'
        # 需要验证的xls文件
        self.verification_file = verification_file
        # 是否需要过滤以及验证成功的sku族
        self.filter = filter

        # 加载的需要验证的xls文件
        self.verification_workbook = xlrd.open_workbook(self.verification_file)
        self.verification_worksheet = self.verification_workbook.sheets()[0]

        # 代理
        self.proxies = {'https': 'https://%s@proxy.crawlera.com:8010/' % api_key,
                        'http': 'http://%s@proxy.crawlera.com:8010/' % api_key}

        # 判断是是否存在验证成功的文件，存在在直接加载，不存在则新建
        if os.path.isfile(self.save_file):
            self.new_workbook = openpyxl.load_workbook(self.save_file)
            self.new_sheet = self.new_workbook.worksheets[0]
        else:
            self.new_workbook = openpyxl.Workbook()
            self.new_sheet = self.new_workbook.worksheets[0]
            self.new_sheet.title = '验证成功'

        self.lock = threading.Lock()
        # 线程池

    def incision_sku(self):
        """
        切割sku族的生成器，
        每个sku族切割成一个list
        [['MH1503112002-2XL', 'B00UKJ3H56'], ['MH1503112002-3XL', 'B00UKJ3HL0'], ['MH1503112002-L', 'B00UKJ3H3S'], ['MH1503112002-XL', 'B00UKJ3H7O'], ['MH1503112002-XS', 'B00UKJ3H5Q']]
        :return:
        """
        rows_list = []
        sku_zu = ''
        for i in range(self.verification_worksheet.nrows):
            if i == 0:
                continue
            rows = self.verification_worksheet.row_values(i)
            if sku_zu == '':
                sku_zu = rows[0].split('-')[0]
                rows_list.append(rows)
            else:
                # 执行多线程函数
                if rows[0].split('-')[0] == sku_zu:
                    rows_list.append(rows)
                else:
                    # 执行多线程函数
                    yield rows_list
                    sku_zu = rows[0].split('-')[0]
                    rows_list = [rows]

    def start(self, pool_size):
        """
        开始程序
        :return:
        """
        pool = ThreadPoolExecutor(pool_size)
        resule = [pool.submit(self.distribute_sku, row_list) for row_list in self.incision_sku()]
        for i in resule:
            i.add_done_callback(self.save_to_file)
        wait(resule)

    def distribute_sku(self, rows_list):
        """
        拆分sku分发，给verification函数进行验证
        :param rows_list:[['MH1503112002-2XL', 'B00UKJ3H56'], ['MH1503112002-3XL', 'B00UKJ3HL0'], ['MH1503112002-L', 'B00UKJ3H3S'], ['MH1503112002-XL', 'B00UKJ3H7O'], ['MH1503112002-XS', 'B00UKJ3H5Q']]
        """
        data_list = []
        if self.filter:
            for row in rows_list:
                url = 'https://www.amazon.com/dp/%s' % row[1]
                html = self.requests_html(url)
                if html:
                    if html.find('Amazon Best Sellers Rank') != -1:
                        title = self.handel_title(html)
                        row.append(title)
                        data_list.append(row)
                    else:
                        print('验证失败', row)
            return data_list
        else:
            for row in rows_list:
                url = 'https://www.amazon.com/dp/%s' % row[1]
                html = self.requests_html(url)
                if html:
                    if html.find('Amazon Best Sellers Rank'):
                        title = self.handel_title(html)
                        row.append(title)
                        return rows_list
                    else:
                        print('验证失败', row)
            return []

    def save_to_file(self, future):
        """
        保存数据到excel表格
        :param future:
        :return:
        """
        data_list = future.result()
        if data_list:
            title = data_list[0][-1]
            # 加锁
            self.lock.acquire()
            for data in data_list:
                if len(data) < 3:
                    data.append(title)
                print('验证成功:', data)
                self.new_sheet.append(data)
            self.new_workbook.save(self.save_file)
            self.lock.release()
            # 释放锁

    def handel_title(self, html):
        """
        解析请求回来的页面，返回解析出来的title
        :param html:
        :return:
        """
        soup = BeautifulSoup(html, 'lxml')
        title_tag = soup.find(name='span', id='productTitle')
        if title_tag:
            title = title_tag.text.strip()
            return title
        else:
            return ''

    def requests_html(self, url):
        """
        负责请求页面
        :param url:
        :return:
        """
        r = requests.get(url, proxies=self.proxies, verify=False)
        if r.status_code == 200:
            return r.text
        else:
            print('访问页面失败,请检查网络！')


def main(file, filter, api_key, pool_size):
    help = '''
        **************************************************************************

                                亚马逊爬虫-ScrapyHub

        **************************************************************************
        '''
    print(help)
    try:
        excel_file = file
        s = Spider(excel_file, filter, api_key)
        s.start(int(pool_size))
        input('程序执行完毕，!按任意键退出...')
    except Exception as e:
        print('出现错误：', e)
        input('...........................')


if __name__ == '__main__':
    con = configparser.ConfigParser()
    con.read('config.ini', encoding='utf-8')

    # 需要验证的exce文件
    excel_file = con.get('settings', 'excel_file')
    if not os.path.isfile(excel_file):
        print(excel_file, '文件不存在！')
        sys.exit(0)

    # 是否需要过滤
    filter_text = con.get('settings', 'filter')
    if filter_text == 'yes':
        filter = True
    elif filter_text == 'no':
        filter = False
    else:
        print(filter_text, 'filter输入有误，请重新输入!')
        sys.exit(0)
    # api_key
    api_key = con.get('settings', 'api_key')
    # 线程数
    pool_size = int(con.get('settings', 'pool_size'))
    # 执行
    main(excel_file, filter, api_key, pool_size)

