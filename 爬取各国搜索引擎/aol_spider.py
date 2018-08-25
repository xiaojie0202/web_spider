from selenium import webdriver
import requests
import re
from concurrent.futures import ThreadPoolExecutor, wait
import threading

lock = threading.Lock()
lock2 = threading.Lock()
aol_file = open('aol.txt', 'w+', encoding='utf-8')

url_link_all = set()  # 存放所有的解析出来的uerl
erro_url = set()  # 存放requests为解析出来的url
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
}


def aol_spider():
    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    driver.get(url='https://www.aol.com/')
    input('输入关键字完毕后按回车键盘继续---------->')
    title = driver.title.replace(' - AOL Search Results', '')
    print('您输入的关键字是------------------------>:', title)
    url_link_set = set()
    count_page = 1
    while True:
        all_a = driver.find_elements_by_xpath('//div[@id="web"]//ol//a[@referrerpolicy="origin"]')
        for i in all_a:
            if i:
                link = i.get_attribute("href")
                url_link_set.add(link)
        if count_page == 100:
            break

        if 'Next' in driver.page_source:
            print('当前页面第%s页' % count_page)
            next_page_href = driver.find_element_by_link_text("Next").get_attribute("href")
            driver.get(url=next_page_href)
            count_page += 1
        else:
            break


    pool = ThreadPoolExecutor(10)
    futer = [pool.submit(parse_url, url) for url in url_link_set]
    wait(futer)

    del url_link_set
    print('待重新验证url-----------------------||||||||||||||||||||||||||||||||||||||||||||||||||||>', len(erro_url))
    for i in range(10):
        futer = [pool.submit(parse_url, url) for url in handel_tow()]
        wait(futer)
        print('待重新验证url-----------------------||||||||||||||||||||||||||||||||||||||||||||||||||||>', len(erro_url))

    # 先把requests解析出来的url存放进去
    for i in url_link_all:
        aol_file.write('%s\n' % i)
        aol_file.flush()
    driver.set_page_load_timeout(10)
    temp_url = []
    driver.delete_all_cookies()
    while True:
        if erro_url:
            for i in range(20):
                try:
                    url = erro_url.pop()
                    newwindow = 'window.open("%s");' % url
                    driver.execute_script(newwindow)
                except Exception:
                    break
            windows = driver.window_handles[0]
            for i in driver.window_handles[1:]:
                try:
                    driver.switch_to.window(i)
                    url = driver.current_url
                    if not url.startswith('http://r.search.aol.com/') and not url.startswith(
                            'https://r.search.aol.com/'):
                        if url not in temp_url:
                            aol_file.write('%s\n' % url)
                            aol_file.flush()
                            print('真实url------->', url)
                            temp_url.append(url)
                    driver.close()
                except Exception:
                    try:
                        url = driver.current_url
                        if not url.startswith('http://r.search.aol.com/') and not url.startswith(
                                'https://r.search.aol.com/'):
                            aol_file.write('%s\n' % url)
                            aol_file.flush()
                            print('真实url------->', url)
                        driver.close()
                    except Exception:
                        driver.close()
            driver.switch_to.window(windows)
            driver.delete_all_cookies()
            print('待重新验证url-----------------------||||||||||||||||||||||||||||||||||||||||||||||||||||>', len(erro_url))
        else:
            break
    aol_file.close()
    driver.close()
    # # 退出整个浏览器
    driver.quit()


def parse_url(url):
    try:
        response = requests.get(url=url, headers=headers, timeout=30)
        if response.status_code == 200:
            url_group = re.search(r'window.location.replace\("(?P<url>.+)"\)', response.text)
            if url_group:
                url = url_group.group('url')
                print('真实url---------》', url)
                url_link_all.add(url)
    except Exception:
        if not url.startswith('http://r.search.aol.com/') and not url.startswith('https://r.search.aol.com/'):
            url_link_all.add(url)
            print('真实url---------》', url)
        else:
            print('待重新验证url---->', url)
            erro_url.add(url)


def handel_tow():
    two_erro_url_list = []
    for i in range(len(erro_url)):
        two_erro_url_list.append(erro_url.pop())

    return two_erro_url_list


if __name__ == '__main__':
    aol_spider()
    aol_file.close()
    input('程序执行完毕，请查看当前目录下"aol.txt"文件，按任意键退出')
