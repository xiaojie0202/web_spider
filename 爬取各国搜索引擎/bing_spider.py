from selenium import webdriver


def bing_spider():
    bing_file = open('bing_url.txt', 'w+', encoding='utf-8')
    # 初始化一个Chromedriver用来驱动 Chrome
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # 请求网页
    driver.get(url='http://cn.bing.com/')
    input('输入关键字完毕后按任意键继续---------->')
    title = driver.title.replace(' - 国际版 Bing', '')
    print('您输入的关键字是:', title)
    nex_url = ''
    a_link = []
    page_count = 0
    while True:
        all_a = driver.find_elements_by_xpath('//ol[@id="b_results"]//a[@target="_blank" and @h]')
        for a in all_a:
            link = a.get_attribute('href')
            if link not in a_link:
                if link.find('bing.com') == -1:
                    bing_file.write('%s\n' % link)
                    bing_file.flush()
                    print('真实url---->:%s' % link)
                    a_link.append(link)
        if driver.current_url == nex_url:
            break
        if page_count == 70:
            break
        nex_url = driver.current_url
        next_btn = driver.find_element_by_xpath('//a[@title="Next page"]')
        driver.get(next_btn.get_attribute('href'))
        page_count += 1
    bing_file.close()
    driver.close()
    driver.quit()


if __name__ == '__main__':
    bing_spider()
    input('程序执行完毕，请查看当前目录下"bing_url.txt"文件，按任意键退出')