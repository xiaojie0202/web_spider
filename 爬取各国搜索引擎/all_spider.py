from selenium import webdriver
import requests
import re
from concurrent.futures import ThreadPoolExecutor, wait
import time
import os
from selenium.common.exceptions import NoSuchElementException

WEBDRIVER = r'E:\SDE\webdriver\chromedriver2.39.exe'


class BaseSpider(object):
    def __init__(self, gjz_file):
        self.gjz_file = open(gjz_file, 'r', encoding='utf-8')
        self.driver = webdriver.Chrome(executable_path=WEBDRIVER)
        self.file_name = 'result.txt'

    def start(self):
        pass

    def get_page(self, gjz):
        pass


class AolSpider(BaseSpider):
    """
    https://www.aol.com/
    """

    def __init__(self, gjz_file):
        super(AolSpider, self).__init__(gjz_file)
        self.url_link_set = set()  # 存放所有未转码的URL
        self.parse_url_set = set()  # 存放解析出来的真正url
        self.erro_url = set()  # 存放未解析出来错误的url
        self.pool = ThreadPoolExecutor(10)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }

    def start(self):
        count = 1
        for gjz in self.gjz_file.readlines():
            self.url_link_set = set()  # 存放所有未转码的URL
            self.parse_url_set = set()  # 存放解析出来的真正url
            self.get_page(gjz)
            count += 1
        self.driver_parse_url()
        self.driver.close()
        self.driver.quit()

    def get_page(self, gjz):
        """
        请求搜索关键字页面
        :param gjz: 需要搜索的关键字
        """
        self.driver.get(url='https://search.aol.com/aol/search?s_chn=prt_bon&q=%s&s_it=comsearch' % gjz.strip())
        title = self.driver.title.replace(' - AOL Search Results', '')
        print('当前的关键字是------------------------>:', title)
        self.get_all_url()

    def get_all_url(self):
        """
        解析出来搜索关键字的所有url（非关键字真实url）， 添加都url_link_set的集合中
        """
        count_page = 1
        while True:
            all_a = self.driver.find_elements_by_xpath('//div[@id="web"]//ol//a[@referrerpolicy="origin"]')
            for i in all_a:
                if i:
                    link = i.get_attribute("href")
                    self.url_link_set.add(link)
            if count_page == 70:
                break

            if 'Next' in self.driver.page_source:
                print('当前页面第%s页' % count_page)
                next_page_href = self.driver.find_element_by_link_text("Next").get_attribute("href")
                self.driver.get(url=next_page_href)
                count_page += 1
            else:
                break
        self.get_result_url()
        self.anew_result_url()

    def get_result_url(self):
        """
        获取页面解析出来的真正url
        :return:
        """
        print(self.url_link_set)
        futer = [self.pool.submit(self.parse_url, url) for url in self.url_link_set]
        wait(futer)
        print('待重新验证url-----------------------||||||||||||||||||||||||||||||||||||||||||||||||||||>',
              len(self.erro_url))

    def anew_result_url(self):
        """重新验证错误错误的url， requewsts方式"""
        for i in range(10):
            futer = [self.pool.submit(self.parse_url, url) for url in self.handel_tow()]
            wait(futer)
            print('待重新验证url-----------------------||||||||||||||||||||||||||||||||||||||||||||||||||||>',
                  len(self.erro_url))

        self.save_gjz_file()

    def parse_url(self, url):
        """
        解析
        :param url:
        :return:
        """
        try:
            response = requests.get(url=url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                url_group = re.search(r'window.location.replace\("(?P<url>.+)"\)', response.text)
                if url_group:
                    url = url_group.group('url')
                    print('真实url---------》', url)
                    self.parse_url_set.add(url)
        except Exception:
            if not url.startswith('http://r.search.aol.com/') and not url.startswith('https://r.search.aol.com/'):
                self.parse_url_set.add(url)
                print('真实url---------》', url)
            else:
                print('待重新验证url---->', url)
                self.erro_url.add(url)

    def handel_tow(self):
        """吧错误url提取出来放入新的list中，进行二次验证"""
        two_erro_url_list = []
        for i in range(len(self.erro_url)):
            two_erro_url_list.append(self.erro_url.pop())
        return two_erro_url_list

    def save_gjz_file(self):
        """
        保存目前解析出来的正确url到文件
        :return:
        """
        with open(self.file_name, 'a+') as f:
            for i in self.parse_url_set:
                f.write('%s\n' % i)
        self.parse_url_set = set()

    def driver_parse_url(self):
        """利用浏览器解析出错误的url"""
        self.driver.set_page_load_timeout(10)
        temp_url = []
        self.driver.delete_all_cookies()
        with open(self.file_name, 'a+') as f:
            while True:
                if self.erro_url:
                    for i in range(20):
                        try:
                            url = self.erro_url.pop()
                            newwindow = 'window.open("%s");' % url
                            self.driver.execute_script(newwindow)
                        except Exception:
                            break
                    windows = self.driver.window_handles[0]
                    for i in self.driver.window_handles[1:]:
                        try:
                            self.driver.switch_to.window(i)
                            url = self.driver.current_url
                            if not url.startswith('http://r.search.aol.com/') and not url.startswith(
                                    'https://r.search.aol.com/'):
                                if url not in temp_url:
                                    f.write('%s\n' % url)
                                    f.flush()
                                    print('真实url------->', url)
                                    temp_url.append(url)
                            self.driver.close()
                        except Exception:
                            try:
                                url = self.driver.current_url
                                if not url.startswith('http://r.search.aol.com/') and not url.startswith(
                                        'https://r.search.aol.com/'):
                                    f.write('%s\n' % url)
                                    f.flush()
                                    print('真实url------->', url)
                                self.driver.close()
                            except Exception:
                                self.driver.close()
                    self.driver.switch_to.window(windows)
                    self.driver.delete_all_cookies()
                    print('待重新验证url-----------------------||||||||||||||||||||||||||||||||||||||||||||||||||||>',
                          len(self.erro_url))
                else:
                    break


class BaiduSpider(BaseSpider):
    """
    https://www.baidu.com/s?wd=小杰
    """

    def __init__(self, gjz_file):
        super(BaiduSpider, self).__init__(gjz_file)
        self.pool = ThreadPoolExecutor(20)
        self.result_url = set()  # 存放真实url

    def start(self):
        count = 1
        for gjz in self.gjz_file.readlines():
            self.result_url = set()  # 存放真实url
            self.get_page(gjz)
            count += 1
        self.driver.close()
        self.driver.quit()

    def get_page(self, gjz):
        """获取关键字页面"""
        self.driver.get(url='https://www.baidu.com/s?wd=%s' % gjz.strip())
        title = self.driver.title.replace('_百度搜索', '')
        print('当前关键字是-------------》:', title)
        self.get_gjz_page()

    def get_gjz_page(self):
        """翻页，并把所有的url存到url_link list中"""
        url_link = set()
        page_count = 1
        while True:
            print('当前页数:%s' % page_count)
            # 解析出来当前页面的所有url
            all_a_tag = self.driver.find_elements_by_xpath('//a[@href]')  # 所有的a标签
            for a_tag in all_a_tag:
                if a_tag:
                    href = a_tag.get_attribute('href')
                    if href.startswith('http://www.baidu.com/link?') or href.startswith('https://www.baidu.com/link?'):
                        url_link.add(href)
            # 点击下一页
            if self.driver.page_source.find('下一页') != -1:
                page_count += 1
                next_page_href = self.driver.find_element_by_link_text("下一页>").get_attribute("href")
                self.driver.get(url=next_page_href)
            else:
                break

        fulter = [self.pool.submit(self.handel_baidu_url, url) for url in url_link]
        wait(fulter)

        with open(self.file_name, 'a+') as f:
            for i in self.result_url:
                f.write('%s\n' % i)
                f.flush()

    def pares_page_url(self):
        """
        解析出来当前页面的所有url
        :param driver:
        :return:
        """
        url_link = set()
        all_a_tag = self.driver.find_elements_by_xpath('//a[@href]')  # 所有的a标签
        # 解析出来当前页面所有url
        for a_tag in all_a_tag:
            if a_tag:
                href = a_tag.get_attribute('href')
                if href.startswith('http://www.baidu.com/link?') or href.startswith('https://www.baidu.com/link?'):
                    url_link.add(href)
        return list(url_link)

    def handel_baidu_url(self, url):
        try:
            response = requests.get(url=url, timeout=20)
            print('真实url----->', response.url)
            if response.url.find('.baidu.com') == -1:
                self.result_url.add(response.url)
        except Exception:
            pass


class BingSpider(BaseSpider):
    """
    https://cn.bing.com/search?q=%E4%B8%83%E5%A4%95&form=QBLHCN
    """

    def __init__(self, gjz_file):
        super(BingSpider, self).__init__(gjz_file)

    def start(self):
        count = 1
        self.driver.delete_all_cookies()
        for gjz in self.gjz_file.readlines():
            self.get_page(gjz)
            count += 1

        self.driver.close()
        self.driver.quit()

    def get_page(self, ajz):
        filter_text = 'Your country or region requires a strict Bing SafeSearch setting'
        self.driver.get(url='https://cn.bing.com/?FORM=BEHPTB&ensearch=1')
        self.driver.execute_script("document.getElementById('est_en').click()")
        time.sleep(1)
        self.driver.execute_script("document.getElementById('sb_form_q').value = '{0}'".format(ajz.strip()))
        time.sleep(1)
        self.driver.execute_script("document.getElementById('sb_form_go').click()")
        title = self.driver.title.replace(' - 国际版 Bing', '')
        print('您输入的关键字是:', title)
        page_count = 0
        result_url = []
        while True:
            all_a = self.driver.find_elements_by_xpath('//ol[@id="b_results"]//a[@target="_blank" and @h]')
            for a in all_a:
                link = a.get_attribute('href')
                if link.find('bing.com') == -1 and link.find('www.microsofttranslator.com') == -1:
                    result_url.append(link)
                    print('真实url---->:%s' % link)
            if page_count == 70:
                break
            if self.driver.page_source.find('Check your spelling or try different keywords') != -1 or self.driver.page_source.find('There are no results for') != -1 or self.driver.page_source.find(filter_text) != -1:
                break
            if self.driver.page_source.find('Check your spelling or try different keywords') != -1:
                break
            try:
                next_btn = self.driver.find_element_by_xpath('//a[@title="Next page"]')
            except Exception:
                break
            self.driver.get(next_btn.get_attribute('href'))
            page_count += 1
        with open(self.file_name, 'a+') as f:
            for i in result_url:
                f.write('%s\n' % i)


class DaumSpider(BaseSpider):

    def __init__(self, gjz_file):
        super(DaumSpider, self).__init__(gjz_file)

    def start(self):
        count = 1
        for gjz in self.gjz_file.readlines():
            self.get_page(gjz)
            count += 1

        self.driver.close()
        self.driver.quit()

    def get_page(self, gjz):
        self.driver.get(url='https://search.daum.net/search?w=web&nil_search=btn&DA=NTB&enc=utf8&q=%s' % gjz)
        title = self.driver.title.replace('– Daum 검색', '')
        print('您输入的关键字是:', title)
        with open(self.file_name, 'a+') as f:
            url_link_list = []
            page_count = 0
            while True:
                all_a_tag = self.driver.find_elements_by_xpath(
                    '//ul[@class="list_info clear"]//a[@class="f_link_b" and @target="_blank"]')
                for a_tag in all_a_tag:
                    if all_a_tag:
                        link = a_tag.get_attribute('href')
                        if link not in url_link_list:
                            f.write('%s\n' % link)
                            f.flush()
                            url_link_list.append(link)
                            print('真实url---->:', link)

                if page_count == 100:
                    break
                print('当前第%s页！' % page_count)
                if self.driver.find_element_by_id('pagingArea').get_attribute('innerHTML').find('<em>다음</em>') != -1:
                    next_page_href = self.driver.find_elements_by_xpath('//div[@id="pagingArea"]//a')[-1].get_attribute(
                        'href')
                    self.driver.get(url=next_page_href)
                    page_count += 1
                else:
                    break


class GooNeSpider(BaseSpider):
    def __init__(self, gjz_file):
        super(GooNeSpider, self).__init__(gjz_file)

    def start(self):
        count = 1
        for gjz in self.gjz_file.readlines():
            self.get_page(gjz)
            count += 1
        self.driver.close()
        self.driver.quit()

    def get_page(self, gjz):
        self.driver.get(
            url='https://search.goo.ne.jp/web.jsp?MT=%s&mode=0&sbd=goo001&IE=UTF-8&OE=UTF-8&from=gootop&PT=TOP' % gjz)
        title = self.driver.title.replace('の検索結果 - goo検索', '')
        print('您输入的关键字是:', title)
        with open(self.file_name, 'a+') as f:
            url_link_list = []
            page_count = 1
            while True:
                all_a_tag = self.driver.find_elements_by_xpath('//div[@class="result"]/p[@class="title fsL1"]/a')
                for a in all_a_tag:
                    if a:
                        link = a.get_attribute('href')
                        if link not in url_link_list:
                            f.write('%s\n' % link)
                            f.flush()
                            url_link_list.append(link)
                            print('真实url地址---->', link)
                print('当前第%s页！' % page_count)
                if self.driver.page_source.find("return cc('next_web'") != -1:
                    next_page_href = self.driver.find_elements_by_xpath('//p[@class="fsL1"]/a[@onclick]')[
                        -1].get_attribute(
                        'href')
                    self.driver.get(url=next_page_href)
                    page_count += 1
                else:
                    break


class GoogleSpider(BaseSpider):
    def __init__(self, gjz_file):
        super(GoogleSpider, self).__init__(gjz_file)

    def start(self):
        self.driver.get(url='https://www.google.com.hk/')
        count = 1
        for gjz in self.gjz_file.readlines():
            self.get_page(gjz)
            count += 1
        self.driver.close()
        self.driver.quit()

    def get_page(self, gjz):
        # https://www.google.com.hk/
        self.driver.get(url='https://www.google.com.hk/')
        time.sleep(1)
        self.driver.execute_script("document.getElementById('lst-ib').value='%s'" % gjz.strip())
        time.sleep(1)
        self.driver.execute_script("document.getElementsByName('btnK')[0].click()")
        title = self.driver.title.replace(' - Google 搜索', '')
        print('您输入的关键字是:', title)

        with open(self.file_name, 'a+') as f:
            url_link_list = []
            page_count = 1
            while True:
                all_a_tag = self.driver.find_elements_by_xpath('//a[@ping and @href]')
                for a_tag in all_a_tag:
                    link = a_tag.get_attribute('href')
                    if link not in url_link_list:
                        if link.find('google') == -1:
                            f.write('%s\n' % link)
                            f.flush()
                            url_link_list.append(link)
                            print('真实url--------->%s' % link)
                print('当前第%s页！' % page_count)
                if self.driver.page_source.find('下一页') != -1:
                    next_page_href = self.driver.find_element_by_id("pnnext").get_attribute('href')
                    self.driver.get(url=next_page_href)
                    page_count += 1
                else:
                    break


class YaHooSpider(BaseSpider):
    def __init__(self, gjz_file):
        super(YaHooSpider, self).__init__(gjz_file)

    def start(self):
        count = 1
        self.driver.delete_all_cookies()
        for gjz in self.gjz_file.readlines():
            self.get_page(gjz)
            count += 1
        self.driver.close()
        self.driver.quit()

    def get_page(self, gjz):
        self.driver.get(
            url='https://search.yahoo.com/search?p=%s&fr=yfp-t&fp=1&toggle=1&cop=mss&ei=UTF-8' % gjz.strip())
        title = self.driver.title.replace(' - Yahoo Search Results', '')
        print('您输入的关键字是:', title)
        url_link_set = []
        next_page_url_list = []

        try:
            next_page_href = self.driver.find_element_by_link_text("Next").get_attribute("href")
        except Exception:
            try:
                next_page_href = self.driver.find_element_by_xpath('//a[@class="next"]').get_attribute("href")
            except Exception:
                next_page_href = ''
        yahoo_file = open(self.file_name, 'a+')
        for i in range(1, 70):
            url = re.sub(r'&b=(\d)', '&b=%s' % i, next_page_href)
            if url:
                next_page_url_list.append(url)
        while True:
            if self.driver.page_source.find('Check spelling or type a new query') != -1:
                break
            all_a = self.driver.find_elements_by_xpath('//a[@referrerpolicy="origin"]')
            for i in all_a:
                if i:
                    link = i.get_attribute("href")
                    if link not in url_link_set:
                        if link.find('webcache.googleusercontent.com') == -1 and link.find(
                                'http://cc.bingj.com/cache.aspx') == -1:
                            yahoo_file.write('%s\n' % link)
                            yahoo_file.flush()
                            print('真实url------->', link)
                            url_link_set.append(link)
            try:
                url = next_page_url_list.pop(0)
                print(url)
                self.driver.get(url=url)
                time.sleep(3)
            except IndexError:
                break
        yahoo_file.close()


class YanDexSpider(BaseSpider):
    """
    https://www.yandex.ru/search/?text=小杰
    """

    def __init__(self, gjz_file):
        super(YanDexSpider, self).__init__(gjz_file)

    def start(self):
        count = 1
        for gjz in self.gjz_file.readlines():
            self.get_page(gjz)
            count += 1
        self.driver.close()
        self.driver.quit()

    def get_page(self, gjz):
        self.driver.get(url='https://www.yandex.ru/search/?text=%s' % gjz.strip())
        title = self.driver.title.replace(' — Яндекс: нашлось 484 млн результатов', '')  # дальше
        print('您输入的关键字是:', title)
        url_link_list = []
        yandex_file = open(self.file_name, 'a+')
        while True:
            all_a_tag = self.driver.find_elements_by_xpath('//li[@class="serp-item"]//h2/a')
            for a_tag in all_a_tag:
                if all_a_tag:
                    link = a_tag.get_attribute('href')
                    if link not in url_link_list:
                        yandex_file.write('%s\n' % link)
                        yandex_file.flush()
                        print('真实url---->:', link)

            if self.driver.page_source.find("дальше") != -1:
                next_page_href = self.driver.find_element_by_link_text('дальше').get_attribute('href')
                print(next_page_href)
                self.driver.get(url=next_page_href)
            else:
                break
        yandex_file.close()

def main():
    # print.cfm?article_id=Collectibles / Crafts
    help = '''
            #######################################################################
            #                          请选择搜索引擎                             #
            #######################################################################
            #                   [0] : www.aol.com                                 #
            #                   [1] : www.baidu.com                               #
            #                   [2] : cn.bing.com                                 #
            #                   [3] : www.daum.net                                #
            #                   [4] : www.goo.ne.jp                               #
            #                   [5] : www.google.com                              #
            #                   [6] : www.yahoo.com                               #
            #                   [7] : yandex.ru                                   #
            #######################################################################

        '''
    print(help)
    while True:
        engin = input('请输入搜索的前的序号：')
        if int(engin) in range(0, 8):
            break
        else:
            print('当前搜索引擎不存在')
    while True:
        gjz_file = input('请输入保存关键字的txt文件的绝对路径:')
        if os.path.isfile(gjz_file):
            break
        else:
            print('当前文件不存在！')
    engin_list = [AolSpider, BaiduSpider, BingSpider, DaumSpider, GooNeSpider, GoogleSpider, YaHooSpider, YanDexSpider]
    engin_class = engin_list[int(engin)]
    try:
        a = engin_class(gjz_file=gjz_file)
        a.start()
        print('数据爬取完毕，进行去重操作》》》》》》》》》》》》》》》》')
        with open(a.file_name, 'r') as f:
            url_list = set(f.readlines())
        with open('result.txt', 'w+') as result:
            result.writelines(list(url_list))
        input('程序执行完毕，按回车键退出！。。。')
    except Exception as e:
        print(e)
        input('出现错误，请截图给程序员！')
if __name__ == '__main__':
    # print.cfm?article_id=Collectibles / Crafts
    main()


