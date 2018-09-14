from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options

import time


class RechargeBattle(object):
    """
    暴雪充值
    """

    def __init__(self, username, password, IBAN):
        self.username = username
        self.password = password
        self.IBAN = IBAN
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        self.driver = webdriver.Chrome(executable_path='driver.exe')

    # 绑定IBAN
    def bind_iban(self):
        """
        绑定Iban
        :return:
        """
        self.driver.get(
            url='https://eu.battle.net/login/de/?ref=https://eu.battle.net/account/management/add-payment-method.html&app=bam&cr=true')
        # 输入用户名密码
        emil = self.driver.find_element_by_id('accountName')
        emil.send_keys(self.username)
        passwird = self.driver.find_element_by_id('password')
        passwird.send_keys(self.password)
        if emil.get_attribute('value') == self.username and passwird.get_attribute('value') == self.password:
            print('输入成功')
        else:
            print('输入失败，重新输入')
            self.driver.execute_script("""$("input[name='accountName']").val('%s')""" % self.username)
            self.driver.execute_script("""$("input[name='password']").val('%s')""" % self.username)

        time.sleep(0.5)
        try:
            submit_btn = self.driver.find_element_by_id('submit')
            submit_btn.click()
        except Exception:
            self.driver.execute_script("$('#submit').click()")
        time.sleep(2)
        if self.driver.current_url == 'https://eu.battle.net/account/management/add-payment-method.html':
            try:
                selector = Select(self.driver.find_element_by_id('paymentMethod'))
                print(selector)
                selector.select_by_value('ELV')
            except Exception:
                self.driver.execute_script("$('#paymentMethod').val('ELV')")

            # 输入内容
            bank_name = self.driver.find_element_by_id('accountHolderName')
            bank_name.send_keys('a')

            iban_input = self.driver.find_element_by_id('iban')
            iban_input.send_keys(self.IBAN)

            first_name_input = self.driver.find_element_by_id('address.firstname')
            first_name_input.send_keys('a')

            last_name_input = self.driver.find_element_by_id('address.lastname')
            last_name_input.send_keys('a')

            address_input = self.driver.find_element_by_id('address.address1')
            address_input.send_keys('a')

            city_input = self.driver.find_element_by_id('address.city')
            city_input.send_keys('a')

            zipcode_input = self.driver.find_element_by_id('address.zipcode')
            zipcode_input.send_keys('12345')

            submit_save_iban_btn = self.driver.find_element_by_id('creation-submit')
            submit_save_iban_btn.click()

            if self.driver.current_url == 'https://eu.battle.net/account/management/add-payment-method.html':
                if self.driver.page_source.find('SEPA Direct Debit Mandate') != -1 or self.driver.page_source.find(
                        'SEPA-Lastschrift-Mandat') != -1:
                    submit_save_iban_btn = self.driver.find_element_by_id('creation-submit')
                    submit_save_iban_btn.click()
                    time.sleep(2)
                    print(self.driver.current_url)
                    if self.driver.current_url == 'https://eu.battle.net/account/management/add-payment-method.html?mandateConfirm=true':
                        if self.driver.page_source.find(
                                'Zahlungsmethode hinzugefügt') != -1 or self.driver.page_source.find('已新增付費方式'):
                            return self.username, self.password, self.IBAN

    # 充值
    def chongzhi(self):
        """
        充值
        :return:
        """
        # 充值
        self.driver.get(url='https://eu.battle.net/shop/checkout/subscribe/2751')
        time.sleep(2)
        try:
            chongzhi_btn = self.driver.find_element_by_id('#payment-submit')  # payment-submit
            chongzhi_btn.click()
        except Exception:
            self.driver.execute_script("$('#payment-submit').click()")
        time.sleep(5)
        if self.driver.page_source.find('Thank you!') != -1 or \
                self.driver.page_source.find('謝謝您') != -1 or \
                self.driver.page_source.find(
                    'payment.success.dynamic.purchaseDetails.default.default.default.heading.1') != -1:
            print('充值完毕!')
            return self.username, self.password, self.IBAN
        else:
            return False

    # 《魔獸世界：決戰艾澤拉斯》典藏組合包
    def gm_1(self):

        self.driver.get(url='https://EU.battle.net/shop/checkout/buy/30742')
        time.sleep(5)
        try:
            chongzhi_btn = self.driver.find_element_by_id('#payment-submit')  # payment-submit
            chongzhi_btn.click()
        except Exception:
            self.driver.execute_script("$('#payment-submit').click()")
        time.sleep(5)
        if self.driver.page_source.find('Thank you!') != -1 or \
                self.driver.page_source.find('謝謝您') != -1 or \
                self.driver.page_source.find(
                    'payment.success.dynamic.purchaseDetails.default.default.default.heading.1') != -1:
            print('《魔獸世界：決戰艾澤拉斯》典藏組合包-----购买成功')
            return self.username, self.password, self.IBAN
        else:
            return False

    # 《魔獸世界》數位豪華完整典藏版
    def gm_2(self):
        # 《魔獸世界》數位豪華完整典藏版
        self.driver.get(url='https://eu.battle.net/shop/checkout/buy/39870')
        time.sleep(5)
        if self.driver.page_source.find('Whoa there! First things') != -1 or self.driver.page_source.find(
                '嘿！先從最重要的著') != -1:
            print('需要创建新账号了')
            try:
                create_btn = self.driver.find_element_by_id('upgrade-create-button')
                create_btn.click()
                print(self.driver.current_url)
                time.sleep(3)
            except Exception:
                self.driver.execute_script("$('#upgrade-create-button').click()")
                print(self.driver.current_url)
                time.sleep(3)
        try:
            chongzhi_btn = self.driver.find_element_by_id('#payment-submit')  # payment-submit
            chongzhi_btn.click()
        except Exception:
            self.driver.execute_script("$('#payment-submit').click()")

        time.sleep(5)
        if self.driver.page_source.find('Thank you!') != -1 or \
                self.driver.page_source.find('謝謝您') != -1 or \
                self.driver.page_source.find(
                    'payment.success.dynamic.purchaseDetails.default.default.default.heading.1') != -1:
            print('《魔獸世界》完整典藏版-----购买成功')
            return self.username, self.password, self.IBAN
        else:
            return False

    def close(self):
        self.driver.delete_all_cookies()
        self.driver.close()
        self.driver.quit()


if __name__ == '__main__':
    a = RechargeBattle(username='u7h5DyqaEt@pdc.com', password='sahfuailh262', IBAN='DE04390700200014960900')
    print(a.bind_iban())  # 绑定IBAN
    print(a.chongzhi())  # 充值
    print(a.gm_1())  # 购买
    print(a.gm_2())  # 购买
