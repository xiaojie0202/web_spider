from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, wait
import threading
import requests

url_txt = open('baidu_url.txt', 'w+', encoding='utf-8')
lock = threading.Lock()

url_link_set = set()


def handel_page_url(driver):
    """
    解析出来当前页面的所有url
    :param driver:
    :return:
    """
    url_link = set()
    all_a_tag = driver.find_elements_by_xpath('//a[@href]')  # 所有的a标签
    # 解析出来当前页面所有url
    for a_tag in all_a_tag:
        if a_tag:
            href = a_tag.get_attribute('href')
            if href.startswith('http://www.baidu.com/link?') or href.startswith('https://www.baidu.com/link?'):
                url_link.add(href)
    return list(url_link)


def baidu_spider():
    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    driver.get(url='https://www.baidu.com/')
    input('输入关键字完毕后按回车键继续---------->')
    title = driver.title.replace('_百度搜索', '')
    print('您输入的关键字是:', title)

    # 存放百度url的set集合
    url_link = []
    page_count = 1
    while True:
        print('当前页数:%s' % page_count)
        # 解析出来当前页面的所有url
        url_link.extend(handel_page_url(driver))
        # 点击下一页
        if driver.page_source.find('下一页') != -1:
            page_count += 1
            next_page_href = driver.find_element_by_link_text("下一页>").get_attribute("href")
            driver.get(url=next_page_href)
        else:
            break
    # 存放未转码的url
    url_link = list(url_link)
    print(url_link)
    print(len(url_link))

    # 启用线程进行验证url
    pool = ThreadPoolExecutor(50)
    fulter = [pool.submit(handel_baidu_url, url) for url in url_link]
    wait(fulter)

    for result_url in url_link_set:
        url_txt.write('%s\n' % result_url)
        url_txt.flush()
    # driver.current_url()
    # 关闭当前页面
    driver.close()
    # 退出整个浏览器
    driver.quit()


def handel_baidu_url(url):
    try:
        response = requests.get(url=url, timeout=20)
        print('真实url----->', response.url)
        if response.url.find('.baidu.com') == -1:
            lock.acquire()
            url_link_set.add(response.url)
            lock.release()
    except Exception:
        pass


if __name__ == '__main__':
    baidu_spider()
    input('程序执行完毕，请查看当前目录下"baidu_url.txt"文件，按任意键退出')
