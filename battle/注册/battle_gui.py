from tkinter import ttk
from bs4 import BeautifulSoup
import tkinter
import requests
import json
import tkinter.messagebox
import random
import string
import threading
import inspect
import ctypes
import os


class BattleRes(object):
    """
    注册Battle账号
    """

    def __init__(self, encrypted, password, first_name, last_name, lz_user, lz_pwd, emil_last):
        self.encrypted = encrypted  # 密保
        self.password = password  # 密码
        self.first_name = first_name  # 姓
        self.lase_name = last_name  # 名
        self.lz_user = lz_user
        self.lz_pwd = lz_pwd
        self.emil_last = emil_last
        self.headers = {
            'Host': 'eu.battle.net',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://eu.battle.net/account/creation/de/tos.html?ref=https%253A%252F%252Feu.battle.net%252Faccount%252Fmanagement%252F&style=&country=DEU',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://eu.battle.net'
        }

    def get_verification_code(self, file_bytes):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Connection': 'keep-alive',
            'Host': 'v1-http-api.jsdama.com',
            'Upgrade-Insecure-Requests': '1'
        }
        files = {
            'upload': ('c:/temp/lianzhong_vcode.png', file_bytes, 'image/png')
        }
        data = {
            'user_name': self.lz_user,
            'user_pw': self.lz_pwd,
        }
        r = requests.post(url='http://v1-http-api.jsdama.com/api.php?mod=php&act=upload', data=data,
                          headers=headers, files=files, verify=False)
        data = json.loads(r.text)
        print(data)  # {'data': {'val': 'YCSGOWZ', 'id': 19882254264}, 'result': True}
        return data

    # 报错识别错误的验证码
    def req_code_erro(self, yzm_id):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Connection': 'keep-alive',
            'Host': 'v1-http-api.jsdama.com',
            'Upgrade-Insecure-Requests': '1'
        }

        data = {
            'user_name': self.lz_user,
            'user_pw': self.lz_pwd,
            'yzm_id': yzm_id
        }
        print('验证码报错%s' % yzm_id)
        requests.post(url='http://v1-http-api.jsdama.com/api.php?mod=php&act=error', headers=headers, data=data,
                      verify=False)

    # 注册用户
    def reg_user(self):
        session = requests.Session()
        # 发送请求主要是未来获取cookies
        print('开始一个注册......')
        r1 = session.get(
            url='https://eu.battle.net/account/creation/de/tos.html?ref=https%253A%252F%252Feu.battle.net%252Faccount%252Fmanagement%252F&style=&country=DEU',
            headers=self.headers)

        # 解析出来csftoken
        soup = BeautifulSoup(r1.text, 'lxml')
        csrftoken = soup.find(name='input', id='csrftoken').attrs['value']

        # 构建post请求数据
        emil = '%s%s' % (''.join(random.sample(string.ascii_letters + string.digits, 10)), self.emil_last)
        print(emil)
        data = {
            'csrftoken': csrftoken,
            'country': 'DEU',
            'firstName': self.first_name,
            'lastName': self.lase_name,
            'dobDay': '11',
            'dobMonth': '1',
            'dobYear': '1985',
            'emailAddress': emil,
            'password': self.password,
            'question1': '19',
            'answer1': self.encrypted,
            'receiveNewsSpecialOffersThirdParty': 'on',
            'agreedToPrivacyPolicy': 'on',
            'optimizelyData': '%5B%5D',
        }
        code_data = {'data': {'id': ''}}
        # 判断是否有验证码
        if soup.find(name='img', id='security-image'):
            a = session.get(url='https://eu.battle.net%s' % soup.find(name='img', id='security-image').attrs['src'])
            print('开始识别验证码！')
            code_data = self.get_verification_code(file_bytes=a.content)
            print('验证码识别结果：', code_data)
            if code_data['result']:
                data['captchaInput'] = code_data['data']['val']
            else:
                return False
        # 发送创建账号请求
        response = session.post(url='https://eu.battle.net/account/creation/de/tos.html', headers=self.headers,
                                data=data)
        print(response)
        print(response.url)
        if response.status_code == 200 and response.url == 'https://eu.battle.net/account/creation/de/success.html' and response.text.find(
                'Accounterstellung erfolgreich') != -1:
            return emil, self.password, self.encrypted
        else:
            threading.Thread(target=self.req_code_erro, args=(code_data['data']['id'],)).start()
            return False

    # 循环注册，直至注册成功一个账号
    def get_one_user(self):
        while True:
            data = self.reg_user()
            if data:
                return data


class BattleGui(object):

    def __init__(self):
        self.battle_res = None  # 注册类
        self.task = None  # 执行开始注册的线程
        self.result_file = open('注册完毕的账号密码.txt', 'a+', encoding='utf-8')
        self.root = tkinter.Tk()
        self.root_width = 510  # 窗口款多
        self.root_height = 500  # 窗口高度
        self.init_root_wind()  # 初始化主窗口信息

        tkinter.Label(self.root, text='Battle注册机V2.0', font=('黑体', 20), fg='red').pack(side=tkinter.TOP, pady=10)

        # _______________联众账号Frame
        self.lz_frame = tkinter.Frame(self.root)
        self.lz_frame.pack(fill=tkinter.X, padx=12)

        # 联众账号
        tkinter.Label(self.lz_frame, text='联众账号:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.lz_username = tkinter.StringVar()
        self.lz_username_input = tkinter.Entry(self.lz_frame, textvariable=self.lz_username)
        self.lz_username_input.pack(side=tkinter.LEFT, padx=10)

        # 联众密码
        tkinter.Label(self.lz_frame, text='联众密码:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.lz_password = tkinter.StringVar()
        self.lz_password_input = tkinter.Entry(self.lz_frame, textvariable=self.lz_password)
        self.lz_password_input.pack(side=tkinter.LEFT, padx=10)

        # _________________Battle的密码和密码相关
        self.entry_frame = tkinter.Frame(self.root)
        self.entry_frame.pack(fill=tkinter.X, padx=12, pady=10)

        # 设置密码
        tkinter.Label(self.entry_frame, text='设置密码:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.password = tkinter.StringVar()
        self.password_input = tkinter.Entry(self.entry_frame, textvariable=self.password)
        self.password_input.pack(side=tkinter.LEFT, padx=10)

        tkinter.Label(self.entry_frame, text='设置密保:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.encrypted = tkinter.StringVar()
        self.encrypted_input = tkinter.Entry(self.entry_frame, textvariable=self.encrypted)
        self.encrypted_input.pack(side=tkinter.LEFT, padx=10)

        # _____________________________first_name, last_name
        self.name_frame = tkinter.Frame(self.root)
        self.name_frame.pack(fill=tkinter.X, padx=3)

        # first_name
        tkinter.Label(self.name_frame, text='firstname:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.firstname = tkinter.StringVar()
        self.firstname_input = tkinter.Entry(self.name_frame, textvariable=self.firstname)
        self.firstname_input.pack(side=tkinter.LEFT, padx=10)

        # last_name
        tkinter.Label(self.name_frame, text='lastname:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.lastname = tkinter.StringVar()
        self.lastname_input = tkinter.Entry(self.name_frame, textvariable=self.lastname)
        self.lastname_input.pack(side=tkinter.LEFT, padx=10)

        # __________________注册数量，邮箱后缀
        self.reg_emlast_frame = tkinter.Frame(self.root)
        self.reg_emlast_frame.pack(fill=tkinter.X, padx=12, pady=10)

        # 邮箱后缀
        tkinter.Label(self.reg_emlast_frame, text='邮箱后缀:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.emil_last = tkinter.StringVar()
        self.emil_last_input = tkinter.Entry(self.reg_emlast_frame, textvariable=self.emil_last)
        self.emil_last_input.pack(side=tkinter.LEFT, padx=10)

        # 注册数量
        tkinter.Label(self.reg_emlast_frame, text='注册数量:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.register_count = tkinter.StringVar()
        self.regster_count_input = tkinter.Entry(self.reg_emlast_frame, textvariable=self.register_count)
        self.regster_count_input.pack(side=tkinter.LEFT, padx=10)

        # _______________________开始注册数量，按钮相关
        self.fooder_frame = tkinter.Frame(self.root)
        self.fooder_frame.pack(fill=tkinter.X, padx=50)

        # 开始注册按钮
        self.start_register_btn = tkinter.Button(self.fooder_frame, text='开始注册', fg='red',
                                                 command=self.start_register_btn_fun, width=20)
        self.start_register_btn.pack(side=tkinter.LEFT)

        # 停止注册按钮
        self.stop_register_btn = tkinter.Button(self.fooder_frame, text='停止注册', fg='red',
                                                command=self.stop_register_user, width=20)
        self.stop_register_btn.pack(side=tkinter.RIGHT)

        # _____________________注册成功的表格信息
        self.result_Frame = tkinter.Frame(self.root, height=320)
        self.result_Frame.pack(fill=tkinter.X, pady=20)

        # 定义中心列表区域
        self.register_info_list_table = ttk.Treeview(self.result_Frame, show="headings", columns=('邮箱', '密码'))
        self.vbar = ttk.Scrollbar(self.result_Frame, orient=tkinter.VERTICAL,
                                  command=self.register_info_list_table.yview)
        self.register_info_list_table.configure(yscrollcommand=self.vbar.set)
        self.register_info_list_table.column("邮箱", anchor="center", width=245)
        self.register_info_list_table.column("密码", anchor="center", width=245)
        self.register_info_list_table.heading("邮箱", text="邮箱")
        self.register_info_list_table.heading("密码", text="密码")
        self.register_info_list_table.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)

        # 重置上一次的信息
        self.rest_config()
        # __________________主窗口循环事件
        self.root.protocol('WM_DELETE_WINDOW', self.close_win)
        self.root.mainloop()

    # a498432181 zxc123456!
    def rest_config(self):
        if os.path.isfile('battmp.tmp'):
            with open('battmp.tmp', 'r', encoding='utf-8') as f:
                data = json.loads(f.read().strip())
                self.lz_username.set(data.get('lz_user'))
                self.lz_password.set(data.get('lz_pwd'))  # 联众密码
                self.password.set(data.get('password'))  # 注册密码
                self.encrypted.set(data.get('entry'))  # 注册密保
                self.register_count.set(data.get('count'))  # 注册数量
                self.firstname.set(data.get('first_name'))
                self.lastname.set(data.get('last_name'))
                self.emil_last.set(data.get('emil_last'))

    # 判断联众平台账号密码是否正确
    def is_login_lz(self):
        username = self.lz_username.get()
        password = self.lz_password.get()
        data = {
            'user_name': username,
            'user_pw': password
        }
        dd = requests.post(url='http://v1-http-api.jsdama.com/api.php?mod=php&act=point', data=data, verify=False)
        data = json.loads(dd.text)
        print('联众平台是否登陆的api', data)
        if data['result']:
            return True
        else:
            return False

    # 开始注册按钮
    def start_register_btn_fun(self):

        # 判断当前是否有任务执行
        if self.task:
            if self.task.isAlive():
                tkinter.messagebox.showerror('ERRO', '当前有注册任务正在进行，请等待任务结束，或者停止注册！')
                return
        # 判断联众平台账号密码是否正确
        if not self.is_login_lz():
            tkinter.messagebox.showerror('ERRO', '联众平台账号密码错误！')
            return
        else:
            lz_user = self.lz_username.get().strip()  # 联众账号
            lz_pwd = self.lz_password.get().strip()  # 联众密码
            password = self.password.get().strip()  # 注册密码
            entry = self.encrypted.get().strip()  # 注册密保
            count = self.register_count.get().strip()  # 注册数量
            emil_last = self.emil_last.get().strip()  # 邮箱后缀
            first_name = self.firstname.get().strip()  # firstname
            last_name = self.lastname.get().strip()  # last_name
            # 判断password
            if not len(password) >= 8 and len(password) <= 16:
                tkinter.messagebox.showerror('输入有误！', '输入设置密码必须是大于8位小于16位！')
                return
            # 判断密保
            if not len(entry) > 3:
                tkinter.messagebox.showerror('输入有误！', '输入设置密保必须是大于4位！')
                return
            # 判断注册数量
            try:
                count = int(count)
            except ValueError:
                tkinter.messagebox.showerror('输入有误！', '输入注册数量有误！')
                return
            # 判断邮箱
            if not emil_last.startswith('@') and not emil_last.endswith('.com'):
                tkinter.messagebox.showerror('输入有误！', '输入邮箱后边必须以@开头, .com结尾！')
                return
            if not first_name or not last_name:
                tkinter.messagebox.showerror('输入有误！', 'firstname和lastname不能为空！')
                return

            if tkinter.messagebox.askokcancel("Start", "是否开始注册账号，数量为%s?" % count):
                self.battle_res = BattleRes(encrypted=entry, password=password,
                                            first_name=first_name,
                                            last_name=last_name,
                                            lz_user=lz_user,
                                            lz_pwd=lz_pwd,
                                            emil_last=emil_last
                                            )
                self.task = threading.Thread(target=self.register_count_user, args=(count,))
                self.task.start()

    # 线程内的函数， 注册指定数量的账号
    def register_count_user(self, count):
        try:
            for i in range(count):
                emil, password, entryed = self.battle_res.get_one_user()
                self.result_file.write('%s------%s------%s\n' % (emil, password, entryed))
                self.result_file.flush()
                self.register_info_list_table.insert("", "end", values=(emil, password))
            tkinter.messagebox.showinfo('执行注册成功', '%s 个账号注册完毕' % count)
        except Exception as e:
            print(e)
            tkinter.messagebox.showerror('网络链接异常', '%s' % e)

    # 结束正在执行的注册线程任务
    def stop_register_user(self):
        if self.task:
            if self.task.isAlive():
                self.stop_thread(self.task)
                tkinter.messagebox.showinfo('SUCCESS', '结束当前注册任务成功！')
                return

    # 强制结束线程
    def stop_thread(self, thread, exctype=SystemExit):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(thread.ident)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    # 初始化主窗口
    def init_root_wind(self):
        self.root.title('Battle注册机V2.0')
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

    # 窗口关闭前执行的事件
    def close_win(self):
        if tkinter.messagebox.askokcancel("Quit", "是否结束程序?"):
            self.stop_register_user()
            self.result_file.close()
            data = dict(
                lz_user=self.lz_username.get().strip(),
                lz_pwd=self.lz_password.get().strip(),
                password=self.password.get().strip(),
                entry=self.encrypted.get().strip(),
                count=self.register_count.get().strip(),
                emil_last=self.emil_last.get().strip(),
                first_name=self.firstname.get().strip(),
                last_name=self.lastname.get().strip(),
            )
            with open('battmp.tmp', 'w+', encoding='utf-8') as f:
                f.write('%s' % json.dumps(data))
            self.root.destroy()


if __name__ == '__main__':
    a = BattleGui()
