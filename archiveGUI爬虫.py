"""
web.archive.org 爬虫， 适合多出口的服务器
"""
from tkinter.filedialog import askopenfilename
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock, Thread
from tkinter import ttk
from requests_toolbelt.adapters import source
from bs4 import BeautifulSoup
import tkinter
import tkinter.messagebox
import os
import requests
import json
import socket
import time
import random

BASE_DIRS = os.path.dirname(os.path.abspath(__file__))
# 禁词站
NOT_DIR = os.path.join(BASE_DIRS, '禁词站')
# 正规站
YES_DIR = os.path.join(BASE_DIRS, '正规站')
# LOG日志
LOG_TXT = os.path.join(BASE_DIRS, 'log.txt')
# 操作完成的域名
SUCCESS_LOG = os.path.join(BASE_DIRS, '操作完成的域名.txt')

if not os.path.isdir(NOT_DIR):
    os.mkdir(NOT_DIR)
if not os.path.isdir(YES_DIR):
    os.mkdir(YES_DIR)


class ArchiveSpiderGui(object):

    def __init__(self):
        self.thread_pool = None  # 线程池
        self.task = None  # 任务
        self.domain_list = None  # 域名列表
        self.wjc_list = None  # 违禁词列表
        self.ip_list = None  # 所有的出口ip

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
        }
        self.thread_lock = Lock()
        # 初始化GUI
        self.init_gui()

    def init_gui(self):
        self.root = tkinter.Tk()
        self.root_width = 800  # 窗口款多
        self.root_height = 320  # 窗口高度
        self.init_root_wind()  # 初始化主窗口信息
        # _________顶部导入域名按钮， 导入违禁词按钮， 线程数，进程数，开始执行
        self.header_franme = tkinter.Frame(self.root)
        self.header_franme.pack(fill=tkinter.X, padx=80, pady=12)

        # 导入域名按钮
        self.import_domain_btn = tkinter.Button(self.header_franme, text='导入域名', command=self.import_domain_func)
        self.import_domain_btn.pack(side=tkinter.LEFT)
        # 导入违禁词按钮
        self.import_not_btn = tkinter.Button(self.header_franme, text='导入违禁词', command=self.import_not_func)
        self.import_not_btn.pack(side=tkinter.LEFT, padx=10)
        # 导入IP信息
        self.import_ip_btn = tkinter.Button(self.header_franme, text='导入IP地址', command=self.import_ip_func)
        self.import_ip_btn.pack(side=tkinter.LEFT, padx=10)
        # 线程数
        tkinter.Label(self.header_franme, text='线程数:').pack(side=tkinter.LEFT)
        self.thread_value = tkinter.StringVar()
        self.thread_input = tkinter.Entry(self.header_franme, textvariable=self.thread_value, width=5)
        self.thread_input.pack(side=tkinter.LEFT)
        # 重新请求数
        tkinter.Label(self.header_franme, text='请求延时:').pack(side=tkinter.LEFT)
        self.reset_count = tkinter.StringVar()
        self.reset_input = tkinter.Entry(self.header_franme, textvariable=self.reset_count, width=5)
        self.reset_input.pack(side=tkinter.LEFT)
        # 开始执行
        self.start_task_btn = tkinter.Button(self.header_franme, text='开始任务', command=self.start_task_func)
        self.start_task_btn.pack(side=tkinter.LEFT, padx=12)

        self.domain_count = tkinter.StringVar()
        self.domain_count_input = tkinter.Entry(self.header_franme, width=5, textvariable=self.domain_count)
        self.domain_count_input.pack(side=tkinter.LEFT)

        self.domain_count.set(0)

        # __________________底部日志系统
        self.log_frame = tkinter.Frame(self.root)
        self.log_frame.pack(fill=tkinter.X)
        self.log_info = tkinter.Listbox(self.log_frame, width=111, height=13)
        self.vbar = ttk.Scrollbar(self.log_frame, orient=tkinter.VERTICAL, command=self.log_info.yview)
        self.log_info.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.log_info.insert('end', '程序初始化完毕！')

        self.root.mainloop()

    # 窗口关键前
    def on_closing(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    # 初始化主窗口
    def init_root_wind(self):
        self.root.title('ArchiveSpider')
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

    # 导入域名
    def import_domain_func(self):
        domain_info = askopenfilename()
        if not domain_info.endswith('.txt'):
            tkinter.messagebox.showinfo('错误', '请导入TXT文档！')
            return
        try:
            with open(domain_info, 'r', encoding='utf-8') as f:
                d = f.readlines()
                self.domain_list = [i.strip() for i in d]
            self.log_info.insert(0, '域名导入成功！数量:%s' % len(self.domain_list))
            return
        except Exception as e:
            tkinter.messagebox.showerror('错误', '文件读取错误：%s' % e)
            return

    # 导入违禁词
    def import_not_func(self):
        wjc_info = askopenfilename()
        if not wjc_info.endswith('.txt'):
            tkinter.messagebox.showinfo('错误', '请导入TXT文档！')
            return
        try:
            with open(wjc_info, 'r', encoding='utf-8') as f:
                d = f.readlines()
                self.wjc_list = [i.strip() for i in d if i.strip()]
            self.log_info.insert(0, '违禁词导入成功！数量:%s' % len(self.wjc_list))
            return
        except Exception as e:
            tkinter.messagebox.showerror('错误', '文件读取错误：%s' % e)
            return

    # 导入IP信息
    def import_ip_func(self):
        ip_filename = askopenfilename()
        if not ip_filename.endswith('.txt'):
            tkinter.messagebox.showinfo('错误', '请导入TXT文档！')
            return
        try:
            with open(ip_filename, 'r', encoding='utf-8') as f:
                d = f.readlines()
                ip_temp_list = [i.strip() for i in d]
            local_ip = self.get_local_ip()
            for ip in ip_temp_list:
                if ip not in local_ip:
                    self.writh_log('ip导入失败, 本地没有%s' % ip)
                    return
            self.ip_list = ip_temp_list
            self.log_info.insert('end', 'IP导入成功！数量:%s' % len(self.ip_list))
            return
        except Exception as e:
            tkinter.messagebox.showerror('错误', '文件读取错误：%s' % e)
            return

    # 开始任务按钮事件
    def start_task_func(self):
        # 判断域名是否导入
        if not self.domain_list or not self.wjc_list or not self.ip_list:
            tkinter.messagebox.showinfo('错误', '请先导入域名和关键字以及IP后操作！')
            return
        # 判断进程数
        if not self.thread_value.get():
            tkinter.messagebox.showinfo('错误', '请先线程数和进程数后操作！')
            return
        try:
            a = int(self.thread_value.get())
        except Exception as e:
            tkinter.messagebox.showinfo('错误', '线程数和进程输入有误')
            return
        # 判断重新请求次数
        try:
            yanshi = int(self.reset_count.get())
        except Exception as e:
            tkinter.messagebox.showinfo('错误', '重新请求次数输入有误')
            return

        if self.task:
            if self.task.isAlive():
                tkinter.messagebox.showerror('ERRO', '当前有任务正在进行，请等待任务结束')
                return

        self.log_info.insert(0, '开始执行任务！')

        self.task = Thread(target=self.innser_task)
        self.task.start()

    def innser_task(self):
        task_num = int(self.thread_value.get())  # 任务数量
        self.thread_pool = ThreadPoolExecutor(task_num)
        fulter_list = [self.thread_pool.submit(self.mainv2, dommain, 0) for dommain in self.domain_list]
        tkinter.messagebox.showinfo('vvvvvvvvv', '全部任务加入到队列')
        wait(fulter_list)
        tkinter.messagebox.showinfo('vvvvvvvvv', '全部任务执行完毕！')

    def create_session(self):
        # 构建出口IP
        out_sourse = source.SourceAddressAdapter(random.choice(self.ip_list))
        # 创建HTTP会话
        session = requests.session()
        # 指定会话的出口
        session.mount('http://', out_sourse)
        session.mount('https://', out_sourse)
        return session

    def mainv2(self, domain, count):
        try:
            yanshi = int(self.reset_count.get())
            session = self.create_session()
            self.writh_log('[%s]开始获取年数据！' % domain)
            # 获取当前域名那些年有数据
            status, years_list = self.get_years(session=session, domain=domain, count=count)
            time.sleep(yanshi)
            self.writh_log('[%s]获取年数据完毕！' % domain)
            # 如果未获取到年数据
            if not status:
                self.add_domain_count()

                self.writh_log(str(years_list))
                return str(years_list)
            # 获取到年数据
            b = '[%s]获取到所有的年数据:%s' % (domain, str(years_list))
            self.writh_log(b)

            # 获取每年的所有url
            all_url = []
            self.writh_log('[%s]开始获取每年的所有url!' % domain)

            for year in years_list:
                status, url_list = self.get_year_url(domain=domain, year=year, count=count)
                if status:
                    all_url.extend(url_list)
                    self.writh_log('[%s] %s年获取url数量%s' % (domain, year, len(url_list)))
                    time.sleep(yanshi)
                else:  # 获取year年的url失败
                    self.writh_log('[%s]%s年数据获取失败：%s' % (domain, year, url_list))
            self.writh_log('[%s]获取每年的url完毕！' % domain)
            self.writh_log('[%s]获取到总共url数量:%s' % (domain, len(all_url)))

            # 根据url获取到的数据
            data_list = []
            wjc_flag = False
            if not all_url:
                self.add_domain_count()
                return

            try:
                # 访问每个url， 解析出来响应状态吗， title， keywords
                for url in all_url:
                    self.writh_log('[%s] 开始获取title和keywords!' % url)
                    status, data = self.parse_url(url=url)
                    time.sleep(yanshi)
                    self.writh_log('[%s] 获取完毕title和keywords!' % url)
                    session.cookies.clear()
                    if status:
                        data_list.append(data)
                        if not wjc_flag:
                            for wjc in self.wjc_list:
                                if wjc.strip():
                                    if wjc.strip() in data[3] or wjc.strip() in data[4]:
                                        wjc_flag = True
                        self.writh_log('[%s]%s' % (url, str(data)))
                    else:
                        self.writh_log(data)
                data_list.sort()
            except Exception as e:
                self.writh_log('[%s]获取数据出现错误!:%s' % (domain, e))
            finally:
                self.add_domain_count()
                domain_filename = None
                if data_list:
                    if wjc_flag:
                        domain_filename = os.path.join(NOT_DIR, '%s.txt' % domain)
                        with open(domain_filename, 'a+', encoding='utf-8') as f:
                            for data in data_list:
                                f.write('%s\n' % '\t'.join(data[2:]))
                                f.flush()
                    else:
                        domain_filename = os.path.join(YES_DIR, '%s.txt' % domain)
                        with open(domain_filename, 'a+', encoding='utf-8') as f:
                            for data in data_list:
                                f.write('%s\n' % '\t'.join(data[2:]))
                                f.flush()

                try:
                    # 删除空白文件
                    dd = False
                    if domain_filename:
                        with open(domain_filename, 'r', encoding='utf-8') as f:
                            if not f.read().strip():
                                dd = True
                    if dd:
                        os.remove(domain_filename)
                except Exception as e:
                    self.writh_log('[%s]空白文件删除失败！%s' % (domain_filename, e))
            return '%s:vvvvvvvvvvvvvvv执行完毕' % domain
        except Exception as e:
            self.writh_log('[%s]xxxxxxxxxxxxxxxxxxxxxxxxxxx错误大错误%s' % (domain, e))

    # 解析出来当前域名哪些年有数据
    def get_years(self, session, domain, count):
        year_count = 0
        # 保存着count次的所以访问错误信息
        erro_info = []

        print('开始获取年数据X2')
        try:
            # 获取那些年有数据
            print('%s--- 开始获取年数据' % domain)
            response = session.get(
                url='http://web.archive.org/__wb/sparkline?url=%s&collection=web&output=json' % domain,
                headers=self.headers, timeout=10)
            print('%s--- 获取完毕年数据' % domain)

            if response.status_code == 200:
                return True, list(json.loads(response.text).get('years').keys())
            else:
                year_count += 1
                erro_info.append('访问错误，状态码:%s' % response.status_code)
        except Exception as e:
            print('%s--- 获取年数据出现异常' % domain)
            year_count += 1
            erro_info.append('访问出现异常: %s' % e)

        return False, '[%s]年数据获取失败！%s' % (domain, str(erro_info))

    # 解析出来当前年的所有日期，并拼接成url
    def get_year_url(self, domain, year, count):
        # 存放解析出来的url
        url_list = []
        # 存放错误信息
        erro_list = []
        try:
            session = self.create_session()
            response = session.get(
                url='http://web.archive.org/__wb/calendarcaptures?url=%s&selected_year=%s' % (domain, year),
                headers=self.headers, timeout=10)
            if response.status_code == 200:
                json_dict = json.loads(response.text)
                for month in json_dict:
                    for day in month:
                        for day_time in day:
                            if day_time:
                                # 解析时间
                                url_time_list = day_time.get('ts')
                                # 解析出来指定时间对应的状态码
                                status_code_list = day_time.get('st')
                                for index in range(len(url_time_list)):
                                    status_code = status_code_list[index]
                                    if status_code == 200:
                                        url = 'http://web.archive.org/web/%s/%s' % (url_time_list[index], domain)
                                        url_list.append(url)
                return True, url_list
            else:
                erro_list.append('访问错误，状态码:%s' % response.status_code)
        except Exception as e:
            erro_list.append('访问出现异常: %s' % e)

        return False, '[%s]每年url获取错误%s' % (domain, str(erro_list))

    # 获取url的，响应状态吗， title， keywords
    def parse_url(self, url):
        erro_info = []
        try:
            session = self.create_session()
            response = session.get(url=url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                # title
                title = soup.find(name='title').text.strip() if soup.find(name='title') else 'Title'
                # keywords
                d = soup.find(name='meta', attrs={'name': 'keywords'})
                if not d:
                    d = soup.find(name='meta', attrs={'name': 'Keywords'})
                keywords = d.attrs['content'].strip() if d else '未查询到keywords'
                # 时间
                t = response.url.split('/')[4]
                url_time = t[:4] + '年' + t[4:6] + '月' + t[6:8] + '日'
                return True, [str(response.status_code), t, url_time, title, keywords]
            else:
                erro_info.append('访问错误，状态码:%s' % response.status_code)
        except Exception as e:
            erro_info.append('访问出现异常: %s' % e)

        return False, str(erro_info)

    # 写入LOG文件
    def writh_log(self, log):
        print(log)
        self.log_info.insert(0, log)
        with open(LOG_TXT, 'a+', encoding='utf-8') as f:
            f.write('%s\n' % log)

    # 获取IP地址
    def get_local_ip(self):
        ip_list = []
        addrs = socket.getaddrinfo(socket.gethostname(), None)
        for i in addrs:
            if i[0].name == 'AF_INET':
                ip_list.append(i[4][0])
        return ip_list

    def add_domain_count(self):
        self.thread_lock.acquire()
        self.domain_count.set(int(self.domain_count.get()) + 1)
        self.thread_lock.release()
if __name__ == '__main__':
    a = ArchiveSpiderGui()
