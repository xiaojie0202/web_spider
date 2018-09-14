import tkinter
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os
import tkinter.messagebox
from selenium import webdriver
from selenium.webdriver.support.select import Select
import time
from threading import Thread, Lock


class RechargeBattle(object):
    """
    暴雪充值
    """

    def __init__(self, username, password, IBAN):
        self.username = username
        self.password = password
        self.IBAN = IBAN
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
                if self.driver.page_source.find(
                        'SEPA Direct Debit Mandate') != -1 or self.driver.page_source.findwenshu_spider.py(
                    'SEPA-Lastschrift-Mandat') != -1:
                    submit_save_iban_btn = self.driver.find_element_by_id('creation-submit')
                    submit_save_iban_btn.click()
                    time.sleep(2)
                    print(self.driver.current_url)
                    if self.driver.current_url == 'https://eu.battle.net/account/management/add-payment-method.html?mandateConfirm=true':
                        if self.driver.page_source.find(
                                'Zahlungsmethode hinzugefügt') != -1 or self.driver.page_source.find('已新增付費方式'):
                            return self.username, self.password, self.IBAN

    # 只执行批量充值任务
    def pl_chongzhi(self):
        self.driver.get(url='https://eu.battle.net/login/de/?ref=https://eu.battle.net/shop/checkout/subscribe/2751')
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
        print(self.driver.current_url)
        if self.driver.current_url.startswith('https://eu.battle.net/shop/'):
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

    # 批量只购买《魔獸世界：決戰艾澤拉斯》典藏組合包
    def pl_gm1(self):
        self.driver.get(url='https://eu.battle.net/login/de/?ref=https://eu.battle.net/shop/checkout/buy/30742')
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
        print(self.driver.current_url)
        if self.driver.current_url.startswith('https://eu.battle.net/shop/'):
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

    # 批量只购买《魔獸世界》數位豪華完整典藏版
    def pl_gm2(self):
        self.driver.get(url='https://eu.battle.net/login/de/?ref=https://eu.battle.net/shop/checkout/buy/39870')
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
        print(self.driver.current_url)
        if self.driver.current_url.startswith('https://eu.battle.net/shop/'):
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


class RechargeBattleGui(object):

    def __init__(self):
        self.userinfo_list = None  # 保存账号信息的列表
        self.iban_list = None  # 保存iban码的列表
        self.success_file = '充值成功的账号.txt'
        self.bind_file = '充值成功的账号.txt'
        self.chongzhi_file = '充值成功的账号.txt'
        self.gm1_file = '充值成功的账号.txt'
        self.gm2_file = '充值成功的账号.txt'
        self.task = None

        self.root = tkinter.Tk()
        self.root_width = 800  # 窗口款多
        self.root_height = 600  # 窗口高度

        self.init_root_wind()  # 初始化主窗口信息

        # 顶部标签 30px
        tkinter.Label(self.root, text='Battle批量充值购买', font=('黑体', 20), fg='red').pack(side=tkinter.TOP, pady=10)

        # __________三个按钮, 导入账号信息， 导入IBAN， 开始任务
        self.btn_frame = tkinter.Frame()
        self.btn_frame.pack(fill=tkinter.X, padx=100)

        # 导入账号信息按钮
        self.load_userinfo_btn = tkinter.Button(self.btn_frame, text='导入账号信息', command=self.load_userinfo_func)
        self.load_userinfo_btn.pack(side=tkinter.LEFT)

        # 导入IBAN码按钮
        self.load_iban_btn = tkinter.Button(self.btn_frame, text='导入IBAN码', command=self.load_iban_func)
        self.load_iban_btn.pack(side=tkinter.LEFT, padx=170)

        # 开始任务按钮
        self.start_task_btn = tkinter.Button(self.btn_frame, text='开始整个流程任务', command=self.start_func)
        self.start_task_btn.pack(side=tkinter.LEFT)

        #  ________按钮， 批量绑定IBAN， 批量充值， 批量购买1， 批量购买2， 批量绑定+充值， 批量绑定+批量充值+ 购买1， 批量绑定+批量充值+ 购买2
        self.btn_frame2 = tkinter.Frame(self.root)
        self.btn_frame2.pack(fill=tkinter.X, pady=20)

        # 批量绑定IBAN
        self.pl_bing_iban = tkinter.Button(self.btn_frame2, text='批量绑定IBAN', command=self.pl_bing_iban_func)
        self.pl_bing_iban.pack(side=tkinter.LEFT)

        # 批量充值
        self.pl_chongzhi_btn = tkinter.Button(self.btn_frame2, text='批量充值', command=self.pl_chongzhi_func)
        self.pl_chongzhi_btn.pack(side=tkinter.LEFT)

        # 批量购买《魔獸世界：決戰艾澤拉斯》典藏組合包
        self.pl_gm1_btn = tkinter.Button(self.btn_frame2, text='批量购买典藏組合包', command=self.pl_gm1_func)
        self.pl_gm1_btn.pack(side=tkinter.LEFT)

        # 批量购买 《魔獸世界》數位豪華完整典藏版
        self.pl_gm2_btn = tkinter.Button(self.btn_frame2, text='批量购买完整典藏版', command=self.pl_gm2_func)
        self.pl_gm2_btn.pack(side=tkinter.LEFT)

        # 批量绑定+充值按钮
        self.bind_chongzhi_btn = tkinter.Button(self.btn_frame2, text='批量绑定+充值', command=self.bind_chongzhi_func)
        self.bind_chongzhi_btn.pack(side=tkinter.LEFT)

        # 批量绑定+批量充值+ 购买1
        self.bing_chongzhi_gm1_btn = tkinter.Button(self.btn_frame2, text='批量绑定+充值+典藏組合包',
                                                    command=self.bing_chongzhi_gm1_func)
        self.bing_chongzhi_gm1_btn.pack(side=tkinter.LEFT)

        # 批量绑定+充值+购买2
        self.bind_chongzi_gm2_tbn = tkinter.Button(self.btn_frame2, text='批量绑定+充值+完整典藏版',
                                                   command=self.bing_chongzhi_gm2_func)
        self.bind_chongzi_gm2_tbn.pack(side=tkinter.LEFT)

        # ___________注册完毕显示账号的东西， 和日志
        self.fooder_frame = tkinter.Frame(self.root)
        self.fooder_frame.pack(fill=tkinter.X)

        # 注册成功的表格
        self.success_table = ttk.Treeview(self.fooder_frame, show="headings", columns=('邮箱', '密码', 'IBAN'), height=20)
        self.vbar = ttk.Scrollbar(self.fooder_frame, orient=tkinter.VERTICAL, command=self.success_table.yview)
        self.success_table.configure(yscrollcommand=self.vbar.set)
        self.success_table.column("邮箱", anchor="center", width=165)
        self.success_table.column("密码", anchor="center", width=150)
        self.success_table.column("IBAN", anchor="center", width=200)
        self.success_table.heading("邮箱", text="邮箱")
        self.success_table.heading("密码", text="密码")
        self.success_table.heading("IBAN", text="IBAN")
        self.success_table.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)

        # 显示日期信息的文本框
        self.log_text = tkinter.Text(self.fooder_frame, width=35)
        self.vbar2 = ttk.Scrollbar(self.fooder_frame, orient=tkinter.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.vbar2.set)

        self.log_text.grid(row=0, column=3, sticky=tkinter.NSEW)
        self.vbar2.grid(row=0, column=4, sticky=tkinter.NS)

        self.root.mainloop()

    # 初始化主窗口
    def init_root_wind(self):
        self.root.title('拼多多批量修改商品价格')

        self.center_window()  # 设置窗口剧中
        self.root.resizable(width=False, height=False)  # 禁止窗口拉伸

    # 设置窗口剧中
    def center_window(self):
        """
        设置窗口剧中
        :param width: 窗口的宽度
        :param height: 窗口的高度
        :return: 自动设置窗口剧中
        """
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (
            self.root_width, self.root_height, (screenwidth - self.root_width) / 2,
            (screenheight - self.root_height) / 2)
        self.root.geometry(size)

    # 导入账号信息按钮方法
    def load_userinfo_func(self):
        # 打开选择文件对话框
        a = askopenfilename()
        if os.path.isfile(a):
            if a.endswith('.txt'):
                with open(a, 'r', encoding='utf-8') as f:
                    data = f.readlines()
                    if len(data[0].split('------')) > 2:
                        self.userinfo_list = data
                        tkinter.messagebox.showinfo('SUCCESS', '账号导入成功！')
                    else:
                        tkinter.messagebox.showerror('导入文件错误！', '导入账号信息文件格式错误！')
            else:
                tkinter.messagebox.showerror('导入文件错误！', '导入文件不是txt文档，请重新导入！')

    # 导入IBAN码按钮方法
    def load_iban_func(self):
        # 打开选择文件对话框
        a = askopenfilename()
        if os.path.isfile(a):
            if a.endswith('.txt'):
                with open(a, 'r', encoding='utf-8') as f:
                    data = f.readlines()
                    if len(data[0]) > 10:
                        self.iban_list = data
                        tkinter.messagebox.showinfo('SUCCESS', 'IBAN导入成功！')
                    else:
                        tkinter.messagebox.showerror('导入文件错误！', '导入IBAN码文件错误！')
            else:
                tkinter.messagebox.showerror('导入文件错误！', '导入文件不是txt文档，请重新导入！')

    # 开始任务按钮函数
    def start_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return

            self.task = Thread(target=self.thread_task)
            self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    # 进行充值的任务函数
    def thread_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始充值任务，充值账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.bind_iban():
                        self.log_text.insert(tkinter.END, 'IBAN绑定成功:%s' % emil)
                    if r.chongzhi():
                        self.log_text.insert(tkinter.END, '充值成功:%s' % emil)
                    if r.gm_1():
                        self.log_text.insert(tkinter.END, '购买典藏組合包：%s' % emil)
                    if r.gm_2():
                        self.log_text.insert(tkinter.END, '购买完整典藏版:%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.success_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '充值购买任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)

    # 批量绑定按钮任务事件
    def pl_bing_iban_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return

            self.task = Thread(target=self.pl_bing_iban_task)
            self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    # 批量绑定任务
    def pl_bing_iban_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始批量绑定IBAN任务，操作账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.bind_iban():
                        self.log_text.insert(tkinter.END, 'IBAN绑定成功:%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.bind_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '绑定IBAN任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)

    # 批量充值按钮的事件
    def pl_chongzhi_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return
            if tkinter.messagebox.askokcancel("Start", "请确认当前账号都以及绑定IBAN完毕才能进行此充值任务！"):
                self.task = Thread(target=self.pl_chongzhi_task)
                self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    # 批量充值任务
    def pl_chongzhi_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始批量充值任务，操作账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.pl_chongzhi():
                        self.log_text.insert(tkinter.END, '充值成功:%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.chongzhi_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '充值任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)

    # 批量购买典藏组合包
    def pl_gm1_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return
            if tkinter.messagebox.askokcancel("Start", "请确认当前账号都已经绑定IBAN和充值完毕才能进行此充值任务！"):
                self.task = Thread(target=self.pl_gm1_task)
                self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    # 批量购买典藏组合包任务
    def pl_gm1_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始批量购买典藏组合包任务，操作账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.pl_gm1():
                        self.log_text.insert(tkinter.END, '购买典藏组合包成功:%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.gm1_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '买典藏组合包任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)

    # 批量购买完整典藏版
    def pl_gm2_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return
            if tkinter.messagebox.askokcancel("Start", "请确认当前账号都已经绑定IBAN和充值完毕才能进行此充值任务！"):
                self.task = Thread(target=self.pl_gm2_task)
                self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    def pl_gm2_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始批量购买完整典藏版任务，操作账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.pl_gm2():
                        self.log_text.insert(tkinter.END, '购买完整典藏版成功:%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.gm2_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '购买完整典藏版任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)

    # 批量绑定IBAN+充值按钮事件
    def bind_chongzhi_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return
            self.task = Thread(target=self.bind_chongzhi_task)
            self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    # 批量绑定IBAN+充值按钮任务
    def bind_chongzhi_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始批量购买完整典藏版任务，操作账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.bind_iban():
                        self.log_text.insert(tkinter.END, '绑定IBAN成功:%s' % emil)
                    if r.chongzhi():
                        self.log_text.insert(tkinter.END, '充值成功:%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.success_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '绑定+充值任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)

    # 绑定+充值+购买典藏组合包任务
    def bing_chongzhi_gm1_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return

            self.task = Thread(target=self.bing_chongzhi_gm1_task)
            self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    # 绑定+充值+购买典藏组合包任务
    def bing_chongzhi_gm1_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始绑定+充值+购买典藏组合包任务，操作账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.bind_iban():
                        self.log_text.insert(tkinter.END, 'IBAN绑定成功:%s' % emil)
                    if r.chongzhi():
                        self.log_text.insert(tkinter.END, '充值成功:%s' % emil)
                    if r.gm_1():
                        self.log_text.insert(tkinter.END, '购买典藏組合包：%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.success_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '绑定+充值+购买典藏组合包任务任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)

    # # 绑定+充值+购买购买完整典藏版任务
    def bing_chongzhi_gm2_func(self):
        if self.userinfo_list and self.iban_list:
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showinfo('当前有任务在执行', '当前有任务在执行!')
                    return

            self.task = Thread(target=self.bing_chongzhi_gm2_task)
            self.task.start()
        else:
            tkinter.messagebox.showerror('错误！', '请先导入账号和IBAN')

    def bing_chongzhi_gm2_task(self):
        try:
            if tkinter.messagebox.askokcancel("Start", "是否开始绑定+充值+购买购买完整典藏版任务，充值账号为%s个?" % len(self.iban_list)):
                for index in range(len(self.iban_list)):
                    iban = self.iban_list[index].strip()
                    emil, password, entrpy = self.userinfo_list[index].strip().split('------')
                    r = RechargeBattle(username=emil, password=password, IBAN=iban)
                    if r.bind_iban():
                        self.log_text.insert(tkinter.END, 'IBAN绑定成功:%s' % emil)
                    if r.chongzhi():
                        self.log_text.insert(tkinter.END, '充值成功:%s' % emil)
                    if r.gm_2():
                        self.log_text.insert(tkinter.END, '购买完整典藏版:%s' % emil)
                    r.close()
                    self.success_table.insert('', 'end', value=(emil, password, iban))
                    with open(self.success_file, 'a+', encoding='utf-8') as f:
                        f.write('%s------%s-----%s-----%s\n' % (emil, password, entrpy, iban))
            tkinter.messagebox.showinfo('任务完毕', '绑定+充值+购买购买完整典藏版任务完毕！')
        except Exception as e:
            tkinter.messagebox.showerror('出现BUG', '出现BUG%s' % e)


if __name__ == '__main__':
    a = RechargeBattleGui()
    # a = RechargeBattle(username='cemRE2nUx8@yopmail.com', password='sahfuailh262', IBAN='DE74390700200014967400')
    # print(a.pl_gm2())
