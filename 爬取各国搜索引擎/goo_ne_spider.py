from selenium import webdriver


def goo_spider():
    goo_file = open('goo.txt', 'w+', encoding='utf-8')
    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    # https://search.goo.ne.jp/web.jsp?MT=%s&mode=0&sbd=goo001&IE=UTF-8&OE=UTF-8&from=gootop&PT=TOP
    driver.get(url='https://www.goo.ne.jp/')
    input('输入关键字完毕后按任意键继续---------->')
    title = driver.title.replace('の検索結果 - goo検索', '')
    print('您输入的关键字是:', title)

    url_link_list = []
    page_count = 1
    while True:
        all_a_tag = driver.find_elements_by_xpath('//div[@class="result"]/p[@class="title fsL1"]/a')
        for a in all_a_tag:
            if a:
                link = a.get_attribute('href')
                if link not in url_link_list:
                    goo_file.write('%s\n' % link)
                    goo_file.flush()
                    url_link_list.append(link)
                    print('真实url地址---->', link)
        print('当前第%s页！' % page_count)
        if driver.page_source.find("return cc('next_web'") != -1:
            next_page_href = driver.find_elements_by_xpath('//p[@class="fsL1"]/a[@onclick]')[-1].get_attribute('href')
            driver.get(url=next_page_href)
            page_count += 1
        else:
            break

    driver.close()
    driver.quit()


if __name__ == '__main__':
    goo_spider()
    input('程序执行完毕，请查看当前目录下"goo.txt"文件，按任意键退出')
