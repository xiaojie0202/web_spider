from selenium import webdriver


def yandex_spider():
    yandex_file = open('yandex.txt', 'w+', encoding='utf-8')
    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    driver.get(url='https://www.yandex.ru/')
    input('输入关键字完毕后按任意键继续---------->')
    title = driver.title.replace(' — Яндекс: нашлось 484 млн результатов', '')  # дальше
    print('您输入的关键字是:', title)

    url_link_list = []
    #
    while True:
        all_a_tag = driver.find_elements_by_xpath('//li[@class="serp-item"]//h2/a')
        for a_tag in all_a_tag:
            if all_a_tag:
                link = a_tag.get_attribute('href')
                if link not in url_link_list:
                    yandex_file.write('%s\n' % link)
                    yandex_file.flush()
                    print('真实url---->:', link)

        if driver.page_source.find("дальше") != -1:
            next_page_href = driver.find_element_by_link_text('дальше').get_attribute('href')
            print(next_page_href)
            driver.get(url=next_page_href)
        else:
            break
    yandex_file.close()
    driver.close()
    driver.quit()


if __name__ == '__main__':
    yandex_spider()
    input('程序执行完毕，请查看yandex.txt文件，按任意键退出！')
