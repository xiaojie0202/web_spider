from selenium import webdriver


def google_spider():
    google_file = open('google.txt', 'w+', encoding='utf-8')
    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    driver.get(url='http://www.google.cn/')
    input('输入关键字完毕后按任意键继续---------->')
    title = driver.title.replace(' - Google 搜索', '')
    print('您输入的关键字是:', title)

    url_link_list = []
    page_count = 1
    while True:
        all_a_tag = driver.find_elements_by_xpath('//a[@ping and @href]')
        for a_tag in all_a_tag:
            link = a_tag.get_attribute('href')
            if link not in url_link_list:
                if link.find('google') == -1:
                    google_file.write('%s\n' % link)
                    url_link_list.append(link)
                    print('真实url--------->%s' % link)
        print('当前第%s页！' % page_count)
        if driver.page_source.find('下一页') != -1:
            next_page_href = driver.find_element_by_id("pnnext").get_attribute('href')
            driver.get(url=next_page_href)
            page_count += 1
        else:
            break

    driver.close()
    driver.quit()


if __name__ == '__main__':
    google_spider()
    input('程序执行完毕，请查看当前目录下"google.txt"文件，按任意键退出')