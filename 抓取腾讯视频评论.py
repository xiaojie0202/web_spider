from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
from bs4 import BeautifulSoup

def get_html(url):
    """
    获取电影的id
    :param url:
    :return:
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('log-level=3')

    # driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe', chrome_options=chrome_options)

    driver.implicitly_wait(20)

    # 请求网页
    driver.get(url=url)
    print('请求页面: %s' % url)
    title = driver.title
    print('当前影视名称：%s' % title)

    js = "var q=document.documentElement.scrollTop=100000"
    driver.execute_script(js)

    element = driver.find_element_by_id("commentIframe")

    print('找到评论页面!')
    driver.switch_to.frame(element)
    driver.execute_script(js)


    driver.execute_script(js)
    click_js = '''$('.J_shortMore').click()'''

    count = 0

    while driver.page_source.find('没有更多评论了') == -1:
        count += 1
        driver.execute_script(click_js)
        driver.execute_script(js)
        time.sleep(0.01)
        print('【SUCCESS】请求完毕%s篇评论！' % count)

    print('【SUCCESS】评论页面请求完毕！')
    html = driver.page_source

    # 关闭当前页面
    driver.close()
    # 退出整个浏览器
    driver.quit()
    # return vid
    # 电影名称 html
    return title, html


def parse_html(html, file):
    soup = BeautifulSoup(html, 'lxml')
    comment_list = soup.find_all(name='div', attrs={'class': 'comment'})
    for comment in comment_list:
        context = comment.find(name='div', attrs={'class': 'comment-content J_CommentContent'})
        if context:
            print('评论:', context.text)
            file.write('%s\n' % context.text)
            file.flush()


if __name__ == '__main__':
    a = '''
        *********************************************************************************
        
                                抓取腾讯视频指定视频的所有评论
        
        *********************************************************************************
    '''
    while True:
        print(a)
        url = input('请输入视频链接(URL):')
        try:
            title, html = get_html(url)
        except WebDriverException as e:
            print('[ERRO]%s' % e)
            continue
        file = open('%s.txt' % title, 'w+', encoding='utf-8')
        parse_html(html, file)
        file.close()
        print('全部评论保存完毕，请查看文件：%s' % '%s.txt' % title)
