from selenium import webdriver
import time
import re


def yahoo_spider():
    yahoo_file = open('yahoo.txt', 'w+', encoding='utf-8')

    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    driver.get(url='https://www.yahoo.com/')
    input('输入关键字完毕后按任意键继续---------->')
    title = driver.title.replace(' - Yahoo Search Results', '')
    print('您输入的关键字是:', title)
    url_link_set = []
    next_page_url_list = []
    next_page_href = driver.find_element_by_link_text("Next").get_attribute("href")

    for i in range(1, 100):
        url = re.sub(r'&b=(\d)', '&b=%s' % i, next_page_href)
        next_page_url_list.append(url)
    while True:
        if driver.page_source.find('Check spelling or type a new query') != -1:
            break
        all_a = driver.find_elements_by_xpath('//a[@referrerpolicy="origin"]')
        for i in all_a:
            if i:
                link = i.get_attribute("href")
                if link not in url_link_set:
                    if link.find('webcache.googleusercontent.com') == -1 and link.find('http://cc.bingj.com/cache.aspx') == -1:
                        yahoo_file.write('%s\n' % link)
                        yahoo_file.flush()
                        print('真实url------->', link)
                        url_link_set.append(link)
        try:
            url = next_page_url_list.pop(0)
            print(url)
            driver.get(url=url)
            time.sleep(3)
        except IndexError:
            break
    yahoo_file.close()
    driver.close()
    # 退出整个浏览器
    driver.quit()


if __name__ == '__main__':
    yahoo_spider()
    input('程序执行完毕，请查看yahoo.txt文件，按任意键退出！')
