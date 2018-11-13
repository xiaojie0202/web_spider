import tkinter.messagebox
import tkinter
import requests
from hashlib import md5
import json
import string
from bs4 import BeautifulSoup
from threading import Thread
import random


# 若快
class RClient(object):
    """
    若快识别验证码
    """

    def __init__(self, username, password):
        self.username = username
        self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = '116179'
        self.soft_key = '5a46d7b6409c41fa8f28803e85fef87a'
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type=7110, timeout=60):
        """
        识别图片
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        while True:
            r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
            if r.status_code == 200:
                print(r.text)
                if r.text.find('Error') == -1:
                    return json.loads(r.text)

    def query_user(self):
        # http://api.ruokuai.com/info.json
        data = {
            'username': self.username,
            'password': self.password
        }
        r = requests.post(url='http://api.ruokuai.com/info.json', data=data, headers=self.headers)
        print(r.text)
        if r.text.find('Error') == -1:
            return True
        else:
            return False


class DigitalmktgGui(object):
    def __init__(self):
        self.rk = None  # RClient 实例
        self.task = None
        self.is_stop = False  # 是否点击停止任务
        self.ppp = 0  # 当前票数
        self.init_gui()

    def init_gui(self):
        self.root = tkinter.Tk()
        self.root_width = 450  # 窗口款多
        self.root_height = 400  # 窗口高度
        self.init_root_wind()  # 初始化主窗口信息

        # _________若快账号密码， 登陆，导入文件，开始处理
        self.header_frame = tkinter.Frame(self.root)
        self.header_frame.pack(fill=tkinter.X, padx=12, pady=12)
        # 若快账号
        tkinter.Label(self.header_frame, text='若快账号:').pack(side=tkinter.LEFT)
        self.rk_username = tkinter.StringVar()
        tkinter.Entry(self.header_frame, textvariable=self.rk_username, width=15).pack(side=tkinter.LEFT)
        # self.rk_username.set('songxtan')
        # 若快密码
        tkinter.Label(self.header_frame, text='若快密码:').pack(side=tkinter.LEFT)
        self.rk_password = tkinter.StringVar()
        tkinter.Entry(self.header_frame, textvariable=self.rk_password, width=15).pack(side=tkinter.LEFT)
        # self.rk_password.set('an337918123')
        # 登陆若快
        self.login_rk_btn = tkinter.Button(self.header_frame, text='登陆若快', command=self.login_rk_func)
        self.login_rk_btn.pack(side=tkinter.LEFT, padx=15)

        # 输入明星ID
        self.hkMaleIdol = tkinter.StringVar()  # 香港男偶像
        self.hkFemaleIdol = tkinter.StringVar()  # 香港女偶像
        self.hkGroupIdol = tkinter.StringVar()  # 香港组合
        self.asiaIdol = tkinter.StringVar()  # 亚洲人气偶像
        frame1 = tkinter.Frame(self.root)
        frame1.pack(fill=tkinter.X, padx=12)

        tkinter.Label(frame1, text='香港男偶像:').grid(row=0, column=0)
        tkinter.Entry(frame1, textvariable=self.hkMaleIdol, width=15).grid(row=0, column=1)

        tkinter.Label(frame1, text='香港女偶像:').grid(row=1, column=0)
        tkinter.Entry(frame1, textvariable=self.hkFemaleIdol, width=15).grid(row=1, column=1, pady=10)

        tkinter.Label(frame1, text='香港组合  :').grid(row=2, column=0)
        tkinter.Entry(frame1, textvariable=self.hkGroupIdol, width=15).grid(row=2, column=1)

        tkinter.Label(frame1, text='亚洲偶像  :').grid(row=3, column=0)
        tkinter.Entry(frame1, textvariable=self.asiaIdol, width=15).grid(row=3, column=1, pady=10)

        tkinter.Button(frame1, text='开始投票', command=self.start).grid(row=1, column=2, padx=100)
        tkinter.Button(frame1, text='停止投票', command=self.stop).grid(row=2, column=2, padx=100)

        frame2 = tkinter.Frame(self.root)
        frame2.pack(fill=tkinter.X)
        self.log_text = tkinter.Text(frame2, width=60, height=15)
        self.log_text.pack()
        self.log_text.insert(0.0, '程序初始化完成\n')

        self.root.mainloop()

    # 初始化主窗口
    def init_root_wind(self):
        self.root.title('digitalmktg投票')
        self.center_window()  # 设置窗口剧中
        # self.root.resizable(width=False, height=False)  # 禁止窗口拉伸

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

    # 登陆按钮事件
    def login_rk_func(self):
        if not self.rk_username.get() or not self.rk_password.get():
            tkinter.messagebox.showinfo('输入有误', '用户名密码不能为空！')
            return
        rk = RClient(self.rk_username.get(), self.rk_password.get())
        if not rk.query_user():
            tkinter.messagebox.showinfo('登陆失败', '用户名密码错误！')
            return
        else:
            self.rk = rk
            tkinter.messagebox.showinfo('登陆成功', '登陆成功')

    def start(self):
        if not self.rk:
            tkinter.messagebox.showinfo('未登陆', '请先登陆若快之后再进行操作！')
            return
        if self.task:
            if self.task.isAlive():
                tkinter.messagebox.showerror('ERRO', '当前有任务正在进行，请先停止任务！')
                return
        self.task = Thread(target=self.start_task)
        self.task.start()
        # Thread(target=self.start_task).start()
        # Thread(target=self.start_task).start()
        # Thread(target=self.start_task).start()
        # Thread(target=self.start_task).start()

    def start_task(self):
        hkMaleIdol = self.hkMaleIdol.get()
        hkFemaleIdol = self.hkFemaleIdol.get()
        hkGroupIdol = self.hkGroupIdol.get()
        asiaIdol = self.asiaIdol.get()
        if hkMaleIdol or hkFemaleIdol or hkGroupIdol or asiaIdol:
            self.log_text.insert(0.0, '开始投票任务!\n')
            self.is_stop = False
            while True:
                if self.is_stop:
                    self.log_text.insert(0.0, '执行完毕：本线程所投票数:%s\n' % self.ppp)
                    tkinter.messagebox.showinfo('SUCCESS', '执行完毕：本线程所投票数:%s' % self.ppp)
                    return
                try:
                    self.tp_igitalmktg(hkMaleIdol, hkFemaleIdol, hkGroupIdol, asiaIdol)
                except Exception as e:
                    self.log_text.insert(0.0, '出现BUG：%s\n' % e)
        else:
            tkinter.messagebox.showinfo('erro', '四个输入框必须有一个有值!')
            return

    # 停止任务
    def stop(self):
        self.is_stop = True

    # 核心业务逻辑
    def tp_igitalmktg(self, hkMaleIdol, hkFemaleIdol, hkGroupIdol, asiaIdol):
        # 先获取tocken
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1; EML-AL00 Build/HUAWEIEML-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.143 Crosswalk/24.53.595.0 XWEB/358 MMWEBSDK/23 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x2607023A) NetType/4G Language/zh_CN'
        }
        session = requests.Session()
        response = session.get(url='https://yahoo.digitalmktg.com.hk/buzz2018/vote?lang=zh-CN', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        tocken = soup.find(name='input', attrs={'name': 'token'}).attrs.get('value')
        response = session.get(
            url='https://yahoo.digitalmktg.com.hk/buzz2018/vote/captcha?lang=zh-CN&v=%s' % str(random.random()),
            headers=headers)
        # with open('1.png', 'wb') as f:
        #     f.write(response.content)
        self.log_text.insert(0.0, '开始识别验证码！\n')
        code = self.rk.rk_create(response.content).get('Result')
        self.log_text.insert(0.0, '验证码识别结果:[%s]\n' % code)
        if not code:
            return

        headers['X-CSRF-Token'] = tocken
        headers['Content-Type'] = 'application/json;charset=UTF-8'
        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['Host'] = 'yahoo.digitalmktg.com.hk'
        headers['Origin'] = 'https://yahoo.digitalmktg.com.hk'
        headers['Referer'] = 'https://yahoo.digitalmktg.com.hk/buzz2018/vote?lang=zh-CN'

        data = {"hkMaleIdol": hkMaleIdol,
                "hkFemaleIdol": hkFemaleIdol,
                "hkGroupIdol": hkGroupIdol,
                "asiaIdol": asiaIdol,
                "tncFlag": "Y",
                "email": '%s@%s.%s' % (''.join(random.sample(string.ascii_letters + string.digits, 10)),
                                       ''.join(random.sample(string.ascii_lowercase, 2)), 'com'),
                "captcha": code.strip(),
                "token": tocken.strip(),
                "deviceRef": str(random.randint(1111111111, 9999999999))
                }
        response = session.post(url='https://yahoo.digitalmktg.com.hk/buzz2018/vote-api?lang=zh-CN', headers=headers,
                                json=data)
        dd = json.loads(response.text)
        if dd.get('code') == 0:
            self.ppp += 1
            self.log_text.insert(0.0, '%s\n' % dd.get('message'))
        else:
            self.log_text.insert(0.0, '%s\n' % dd.get('message'))

        print(response.text)


if __name__ == '__main__':
    DigitalmktgGui()
