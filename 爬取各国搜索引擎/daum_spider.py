from selenium import webdriver


def daum_spider():
    daum_file = open('daum.txt', 'w+', encoding='utf-8')
    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    driver.get(url='https://www.daum.net/')
    """
    https://search.daum.net/search?w=web&nil_search=btn&DA=NTB&enc=utf8&q=PASSWORD
    """
    input('输入关键字完毕后按任意键继续---------->')
    title = driver.title.replace('– Daum 검색', '')
    print('您输入的关键字是:', title)

    url_link_list = []
    page_count = 0
    while True:
        all_a_tag = driver.find_elements_by_xpath('//ul[@class="list_info clear"]//a[@class="f_link_b" and @target="_blank"]')
        for a_tag in all_a_tag:
            if all_a_tag:
                link = a_tag.get_attribute('href')
                if link not in url_link_list:
                    daum_file.write('%s\n' % link)
                    daum_file.flush()
                    url_link_list.append(link)
                    print('真实url---->:', link)

        # if page_count == 100:
        #     break
        print('当前第%s页！' % page_count)
        if driver.find_element_by_id('pagingArea').get_attribute('innerHTML').find('<em>다음</em>') != -1:
            next_page_href = driver.find_elements_by_xpath('//div[@id="pagingArea"]//a')[-1].get_attribute('href')
            driver.get(url=next_page_href)
            page_count += 1
        else:
            break
    daum_file.close()
    driver.close()
    driver.quit()


if __name__ == '__main__':
    daum_spider()
    input('程序执行完毕，请查看当前目录下"daum.txt"文件，按任意键退出')
