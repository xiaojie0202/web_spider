from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
import requests
import pandas as pd


class AuditorSpider(object):

    def __init__(self, filename):
        # 最后数据保存的文件名称
        self.filename = filename
        # 获取数据的url
        self.url = 'https://www.auditor.state.mn.us/Search/CitySearch.aspx'
        # 生成所有的城市ID
        self.city_list = [str(i) for i in range(100, 959)]
        self.city_list.extend(['-1', '-2', '-3'])
        # 生成所有的年份
        self.year_list = [str(i) for i in range(1995, 2017)]
        # 线程池
        self.pool = ThreadPoolExecutor(25)
        # 线程锁
        self.lock = Lock()

    def parse_entity_yesr(self):
        '''
        解析出来所有的城市， 以及所有的年份
        :return:
        '''
        # 发送get请求获取页面信息
        response = requests.get(url=self.url)
        # 判断响应码是否是200
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            # 解析出来所有的entity id
            entity_select_tag = soup.find(name='select', id='Main_csCity_ddlEntity1')
            entity_option_tag_list = entity_select_tag.find_all(name='option')
            for entity_option_tag in entity_option_tag_list:
                entity_id = entity_option_tag.attrs.get('value', '')
                if entity_id:
                    self.city_list.append(entity_id)
            # 解析出来所有的年份
            year_select_tag = soup.find(name='select', id='Main_csCity_ddlYear1')
            year_option_tag_list = year_select_tag.find_all(name='option')
            for year_option_tag in year_option_tag_list:
                year = year_option_tag.attrs.get('value', '')
                if year:
                    self.year_list.append(year)

        else:
            print(response.text)
            raise Exception('请求失败')

    def get_page_info(self, city_id):
        # 发送get请求获取页面信息
        response = requests.get(url=self.url)
        # 跨站请求伪造破解
        VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION = self.parse_scrf(response.text)
        # 解析出来的数据， 保存城市每年的数据
        data_list = []
        for year in self.year_list:
            # 构建post请求数据
            data = {
                '__VIEWSTATE': VIEWSTATE,
                '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                '__EVENTVALIDATION': EVENTVALIDATION,
                'ctl00$Main$csCity$ddlEntity1': city_id,
                'ctl00$Main$csCity$ddlYear1': year,
                'ctl00$Main$csCity$btnSearch1': 'Go'
            }
            # 发送post请求
            response = requests.post(url=self.url, data=data)
            # 跨站请求伪造破解
            VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION = self.parse_scrf(response.text)
            # 解析出来数据
            save_data = self.parse_info(response.text)
            print(save_data)
            # 把数据追缴到data_list
            data_list.extend(save_data)
        # 把数据保存至文件
        self.lock.acquire()
        dd = pd.DataFrame(data_list)
        dd.to_csv(self.filename, mode='a', header=False)
        self.lock.release()

    def parse_info(self, html):
        '''
        解析出来信息
        :param html: 页面html
        :return:  解析出来的信息
        '''
        data_list = []
        soup = BeautifulSoup(html, 'lxml')
        div_tag = soup.find(name='div', id='Main_csCity_pnlResultsHeader1')
        span_tag_list = div_tag.find_all(name='span')

        Entity = span_tag_list[1].text
        County = span_tag_list[3].text
        Year = span_tag_list[5].text
        Population = span_tag_list[-1].text

        table_tag = soup.find(name='table', id='Main_csCity_tblMain')
        tr_list = table_tag.find_all(name='tr')
        for tr in tr_list[3:]:
            td_list = tr.find_all(name='td')
            if len(td_list) > 2:

                Description = tr.find(name='th').text if tr.find(name='th') else ' '
                Amount = td_list[1].text
                Per_Capita = td_list[2].text
                Rank = td_list[3].text

                data_list.append([Entity, County, Year, Population, Description, Amount, Per_Capita, Rank])
        return data_list

    def parse_scrf(self, html):
        '''
        解析出来csrf需要的数据
        :param html: html页面
        :return: 三个值
        '''
        soup = BeautifulSoup(html, 'lxml')
        VIEWSTATE = soup.find(name='input', id='__VIEWSTATE').attrs.get('value')
        VIEWSTATEGENERATOR = soup.find(name='input', id='__VIEWSTATEGENERATOR').get('value')
        EVENTVALIDATION = soup.find(name='input', id='__EVENTVALIDATION').get('value')
        return VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION

    def start(self):
        '''
        开始呈现，创建多线程的任务
        '''
        result = [self.pool.submit(fn=self.get_page_info, city_id=i) for i in self.city_list]
        wait(result)


if __name__ == '__main__':
    a = AuditorSpider(filename='data.csv')
    # a.get_page_info(a.city_list[5])
    a.start()
