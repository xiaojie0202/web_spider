from tkinter import ttk
from tkinter import messagebox
from threading import Thread
from tkinter.filedialog import askdirectory
import requests
import json
import tkinter
import openpyxl
import os
import time
import re


class PddSpider(object):

    def __init__(self):
        self.data = []  # 存放所有筛选出来的店铺url.
        self.mall_id_history = []  # 抓取的店铺历史
        self.log_file = 'log.log'
        self.task = None  # 线程任务
        self.headers = {
            'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
        }
        self.init_gui()

    def init_gui(self):
        self.root = tkinter.Tk()
        self.root_width = 620  # 窗口款多
        self.root_height = 420  # 窗口高度
        self.init_root_wind()  # 初始化主窗口信息

        tkinter.Label(self.root, text='拼多多店铺采集', font=('黑体', 16), fg='red', pady=20).pack()

        frame_1 = tkinter.Frame(self.root)
        frame_1.pack(fill=tkinter.X, padx=12)
        frame_2 = tkinter.Frame(self.root)
        frame_2.pack(fill=tkinter.X, padx=12, pady=20)
        frame_4 = tkinter.Frame(self.root)
        frame_4.pack(fill=tkinter.X, padx=20, pady=12)
        frame_3 = tkinter.Frame(self.root)
        frame_3.pack(fill=tkinter.X, padx=60)

        # 关键字
        tkinter.Label(frame_1, text='关键字:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.gjz = tkinter.StringVar()
        tkinter.Entry(frame_1, textvariable=self.gjz, width=70).pack(side=tkinter.LEFT)

        # 筛选条件-店铺商品数量
        tkinter.Label(frame_2, text='商品数量:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.good_num = tkinter.IntVar()
        tkinter.Entry(frame_2, textvariable=self.good_num, width=8).pack(side=tkinter.LEFT)

        # 筛选条件-店铺总销量
        tkinter.Label(frame_2, text='店铺销量:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.mall_sales = tkinter.IntVar()
        tkinter.Entry(frame_2, textvariable=self.mall_sales, width=8).pack(side=tkinter.LEFT)

        # 筛选条件-当前拼单人数
        tkinter.Label(frame_2, text='拼单人数:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.indent_count = tkinter.IntVar()
        tkinter.Entry(frame_2, textvariable=self.indent_count, width=8).pack(side=tkinter.LEFT)

        # 筛选条件- 抓取页数
        tkinter.Label(frame_2, text='搜索页数:', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.page_count = tkinter.IntVar()
        tkinter.Entry(frame_2, textvariable=self.page_count, width=8).pack(side=tkinter.LEFT)

        # 按钮-开始任务
        tkinter.Button(frame_3, text='开始任务', width=20, command=self.start).pack(side=tkinter.LEFT, padx=40)

        # 按钮-导出数据
        tkinter.Button(frame_3, text='导出数据', width=20, command=self.export_data).pack(side=tkinter.LEFT, padx=40)

        # 日志系统
        # 数据表格
        self.log_listbox = tkinter.Listbox(frame_4, width=80)
        self.vbar = ttk.Scrollbar(frame_4, orient=tkinter.VERTICAL, command=self.log_listbox.yview)
        self.log_listbox.configure(yscrollcommand=self.vbar.set)
        self.log_listbox.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)

        self.root.mainloop()

    # 初始化主窗口
    def init_root_wind(self):
        self.root.title('拼多多数据采集')

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

    # 开始任务按钮监听事件
    def start(self):
        try:
            gjz = self.gjz.get()
            if not gjz:
                messagebox.showinfo('警告', '请先输入关键字再进行操作!')
                return
            if self.task:
                if self.task.isAlive():
                    tkinter.messagebox.showerror('ERRO', '当前有任务正在进行，请等待任务结束')
                    return
            try:
                page_count = self.page_count.get()
                good_num = self.good_num.get()
                mall_sales = self.mall_sales.get()
                indent_count = self.indent_count.get()
            except Exception as e:
                messagebox.showerror('输入有误!', '输入有误:%s' % e)
                return

            if messagebox.askyesno('开始任务', '确认开启任务?'):
                self.data = []
                self.mall_id_history = []
                self.task = Thread(target=self.get_goods, args=(gjz, page_count, good_num, mall_sales, indent_count))
                self.task.start()
        except Exception as e:
            messagebox.showerror('BUG', '出现BUG：%s' % e)
            return

    # 根据关键字搜索商品
    def get_goods(self, gjz, page_count, good_num, mall_sales, indent_count):
        """
        :param gjz:  关键字
        :param page_count:  抓取的页数
        :param good_num:  过滤店铺的商品数量
        :param mall_sales:  过滤的总销量
        :param indent_count: 过滤店铺的拼单数量
        """

        for page in range(1, page_count + 1):
            self.log_listbox.insert(0, '[INFO]开始抓取第%s页\n' % page)
            url = 'http://apiv3.yangkeduo.com/search?q=%s' % gjz
            response = requests.get(url=url, headers=self.headers)
            with open(self.log_file, 'a+', encoding='utf-8') as f:
                f.write('抓取第%s页的商品：%s\n' % (page, response.text))
            # 所有商品的列表
            good_list = json.loads(response.text)

            # IP受到限制
            if self.is_ip(good_list):
                messagebox.askretrycancel('受限', 'IP受到限制，请更换IP')
                continue

            # 开始获取商品
            for good in good_list.get('items'):
                # 商品ID
                goods_id = good['goods_id']
                mall_id = self.get_mall_id(goods_id)
                if mall_id == 10:
                    messagebox.askretrycancel('受限', 'IP受到限制，请更换IP')
                    continue
                if not mall_id:
                    continue
                if mall_id in self.mall_id_history:
                    continue

                self.mall_id_history.append(mall_id)
                self.log_listbox.insert(0, '[INFO]开始获取店铺[%s]信息' % mall_id)
                # 获取店铺信息
                response = requests.get(url='https://api.pinduoduo.com/mall/%s/info' % mall_id, headers=self.headers)
                with open(self.log_file, 'a+', encoding='utf-8') as f:
                    f.write('获取店铺[%s]信息：%s\n' % (mall_id, response.text))
                mall_info = json.loads(response.text)

                # IP受到限制
                if self.is_ip(mall_info):
                    messagebox.askretrycancel('受限', 'IP受到限制，请更换IP')
                    continue

                # 店铺商品数量
                agood_num = mall_info['goods_num']
                if agood_num < good_num:
                    continue

                # 店铺销售量
                amall_sales = mall_info['mall_sales']
                if amall_sales < mall_sales:
                    continue
                self.log_listbox.insert(0, '[INFO]获取到店铺信息:{商品数量:%s, 店铺总销量:%s}' % (good_num, amall_sales))
                self.log_listbox.insert(0, '[info]开始获取店铺的当前拼单人数')
                # 获取店铺的当前拼单数量
                response = requests.post(url='https://api.pinduoduo.com/api/leibniz/mall/groups',
                                         json={"mall_id": mall_id}, headers=self.headers)

                pdd_data = json.loads(response.text)

                # IP受到限制
                if self.is_ip(mall_info):
                    messagebox.askretrycancel('受限', 'IP受到限制，请更换IP')
                    continue

                # 店铺当前拼单数量
                pdd_count = len(pdd_data['result'])
                if pdd_count >= indent_count:
                    self.log_listbox.insert(0, '[SUCCESS]筛选成共的店铺: %s' % mall_id)
                    url = 'https://mobile.yangkeduo.com/mall_page.html?mall_id=%s' % mall_id
                    print(url)
                    if url not in self.data:
                        self.data.append(url)

        messagebox.showinfo('SUCCESS', '任务处理完毕，抓取到店铺数量:%s' % len(set(self.data)))

    # 获取当前商品以拼数量
    def get_mall_id(self, good_id):
        response = requests.get(url='http://mobile.yangkeduo.com/goods.html?goods_id=%s' % good_id, headers=self.headers)
        json_find = re.findall('window.rawData=\s+(?P<n>{.+});', response.text)
        with open(self.log_file, 'a+', encoding='utf-8') as f:
            f.write('根据商品%s获取店铺ID:%s\n' % (good_id, str(json_find)))
        if json_find:
            data = json.loads(json_find[0])
            if not data.get('initDataObj', None):
                return 10
            try:
                mall_id = data['initDataObj']['mall']['mallID']
                return mall_id
            except Exception:
                return False

    # 判断IP是否受到限制
    def is_ip(self, data):
        if data.get('error_code', None):
            if data['error_code'] == 40001:
                return True
        else:
            return False

    # 导出数据
    def export_data(self):
        try:
            dirname = askdirectory()
            t = time.strftime('%Y-%m-%d-%H%M%S', time.localtime())
            if dirname:
                file_path = os.path.join(dirname, '%s.xlsx' % t)
                workbook = openpyxl.Workbook()
                worksheet = workbook.active
                [worksheet.append([dd]) for dd in self.data]
                workbook.save(file_path)
                messagebox.showinfo('导出成功', '导出成功:%s' % file_path)
        except Exception as e:
            messagebox.showinfo('导出失败', '%s' % e)


if __name__ == '__main__':
    PddSpider()
