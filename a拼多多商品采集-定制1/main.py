from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askdirectory
from threading import Thread
# from concurrent.futures import ThreadPoolExecutor, wait
import tkinter
import json
import requests
import re
import os
import openpyxl


class PddSpider(object):
    """
    拼多多数据采集
    """

    def __init__(self):
        self.task = None  # 线程
        self.data_info = []  # 保存获取到的信息，方便导出
        self.init_gui()
        # self.pool = ThreadPoolExecutor(30)

    def init_gui(self):
        self.root = tkinter.Tk()
        self.root_width = 620  # 窗口款多
        self.root_height = 650  # 窗口高度
        self.init_root_wind()  # 初始化主窗口信息

        # 顶部Frame
        top_frame = tkinter.Frame(self.root)
        top_frame.pack(fill=tkinter.X)
        # 展现数据表格的Frame
        botton_frame = tkinter.Frame(self.root)
        botton_frame.pack(fill=tkinter.X)
        # 关键字frame
        top_left_frame = tkinter.Frame(top_frame)
        top_left_frame.pack(side=tkinter.LEFT, padx=12, pady=12)
        # 一堆按钮Frame
        top_right_frame = tkinter.Frame(top_frame)
        top_right_frame.pack(side=tkinter.LEFT)
        # 排序Frame
        sort_frame = tkinter.Frame(top_right_frame)
        sort_frame.pack(fill=tkinter.X, side=tkinter.TOP)
        # 价格区间，销量区间Frame
        qj_frame = tkinter.Frame(top_right_frame)
        qj_frame.pack(fill=tkinter.X, side=tkinter.TOP, pady=20)
        # 过滤页数，拼团数量， 开始 导出 Frame
        butten_frame = tkinter.Frame(top_right_frame)
        butten_frame.pack(fill=tkinter.X, side=tkinter.TOP)

        # 关键字输入框
        self.gjz_text = tkinter.Text(top_left_frame, width=20, height=15)
        self.vbar = ttk.Scrollbar(top_left_frame, orient=tkinter.VERTICAL, command=self.gjz_text.yview)
        self.gjz_text.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)

        # 排序单选框
        tkinter.Label(sort_frame, text='排序:', fg='red', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.sort = tkinter.StringVar()
        tkinter.Radiobutton(sort_frame, variable=self.sort, text='综合', value='default').pack(side=tkinter.LEFT)
        tkinter.Radiobutton(sort_frame, variable=self.sort, text='评分', value='_credit').pack(side=tkinter.LEFT)
        tkinter.Radiobutton(sort_frame, variable=self.sort, text='销量', value='_sales').pack(side=tkinter.LEFT)
        tkinter.Radiobutton(sort_frame, variable=self.sort, text='价格从低到高', value='price').pack(side=tkinter.LEFT)
        tkinter.Radiobutton(sort_frame, variable=self.sort, text='价格从高到低', value='_price').pack(side=tkinter.LEFT)

        # 价格区间
        self.price_start = tkinter.IntVar()
        self.price_end = tkinter.IntVar()
        tkinter.Label(qj_frame, text='价格区间:', fg='red', font=('黑体', 12)).pack(side=tkinter.LEFT, padx=10)
        tkinter.Entry(qj_frame, textvariable=self.price_start, width=5).pack(side=tkinter.LEFT)
        tkinter.Label(qj_frame, text='-', fg='red', font=('黑体', 12)).pack(side=tkinter.LEFT)
        tkinter.Entry(qj_frame, textvariable=self.price_end, width=5).pack(side=tkinter.LEFT)

        # 销量区间
        self.sales_start = tkinter.IntVar()
        self.sales_end = tkinter.IntVar()
        tkinter.Label(qj_frame, text='销量区间:', fg='red', font=('黑体', 12)).pack(side=tkinter.LEFT, padx=10)
        tkinter.Entry(qj_frame, textvariable=self.sales_start, width=5).pack(side=tkinter.LEFT)
        tkinter.Label(qj_frame, text='-', fg='red', font=('黑体', 12)).pack(side=tkinter.LEFT)
        tkinter.Entry(qj_frame, textvariable=self.sales_end, width=5).pack(side=tkinter.LEFT)

        # 页数
        self.page_count = tkinter.IntVar()
        tkinter.Label(butten_frame, text='页数:', fg='red', font=('黑体', 12)).pack(side=tkinter.LEFT, padx=12)
        tkinter.Entry(butten_frame, textvariable=self.page_count, width=5).pack(side=tkinter.LEFT)

        # 拼团数量
        self.pd_filter = tkinter.IntVar()
        tkinter.Label(butten_frame, text='拼团数:', fg='red', font=('黑体', 12)).pack(side=tkinter.LEFT, padx=12)
        tkinter.Entry(butten_frame, textvariable=self.pd_filter, width=5).pack(side=tkinter.LEFT)

        # 开始采集按钮
        tkinter.Button(butten_frame, text='开始采集', command=self.start_cj).pack(side=tkinter.LEFT, padx=12)
        # 导出数据按钮
        tkinter.Button(butten_frame, text='导出数据', command=self.export_info).pack(side=tkinter.LEFT)

        # 数据表格
        self.info = ttk.Treeview(botton_frame, show="headings", columns=('上家ID', '商品名称', '拼团数', '销量', '价格'), height=18)
        self.vbar = ttk.Scrollbar(botton_frame, orient=tkinter.VERTICAL, command=self.info.yview)
        self.info.configure(yscrollcommand=self.vbar.set)
        self.info.column("上家ID", anchor="center", width=150)
        self.info.column("商品名称", anchor="center", width=280)
        self.info.column("拼团数", anchor="center", width=50)
        self.info.column("销量", anchor="center", width=60)
        self.info.column("价格", anchor="center", width=60)

        self.info.heading("上家ID", text="上家ID")
        self.info.heading("商品名称", text="商品名称")
        self.info.heading("拼团数", text="拼团数")
        self.info.heading("销量", text="销量")
        self.info.heading("价格", text="价格")
        self.info.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)

        self.root.protocol('WM_DELETE_WINDOW', self.close_win)
        self.reser_settings()
        self.root.mainloop()

    def close_win(self):
        if tkinter.messagebox.askokcancel("Quit", "是否结束程序?"):
            data = dict(
                sort=self.sort.get(),
                price_start=self.price_start.get(),
                price_end=self.price_end.get(),
                sales_start=self.sales_start.get(),
                sales_end=self.sales_end.get(),
                page_count=self.page_count.get(),
                pd_filter=self.pd_filter.get()
            )
            with open('pdd.tmp', 'w+', encoding='utf-8') as f:
                f.write('%s' % json.dumps(data))
            self.root.destroy()

    def reser_settings(self):
        if os.path.isfile('pdd.tmp'):
            with open('pdd.tmp', 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
                self.sort.set(data.get('sort'))
                self.price_start.set(data.get('price_start'))
                self.price_end.set(data.get('price_end'))
                self.sales_start.set(data.get('sales_start'))
                self.sales_end.set(data.get('sales_end'))
                self.page_count.set(data.get('page_count'))
                self.pd_filter.set(data.get('pd_filter'))

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

    # 开始按钮
    def start_cj(self):
        if self.task:
            if self.task.isAlive():
                tkinter.messagebox.showerror('ERRO', '当前有任务正在进行，请等待任务结束')
                return

        if not self.sort.get():
            tkinter.messagebox.showinfo('未选择排序方式', '请先选择排序方式!')
            return
        if messagebox.askyesno('开始任务', '确认开启任务?'):
            self.task = Thread(target=self.task_router)
            self.task.start()

    # 多线程任务分发器
    def task_router(self):
        try:
            items = self.info.get_children()

            [self.info.delete(item) for item in items]
            # 获取到用户输入的关键字
            gjz_list = [i.strip() for i in self.gjz_text.get(0.0, tkinter.END).split() if i.strip()]
            jgqj = 'price,%s,%s' % (
                self.price_start.get(), self.price_end.get()) if self.price_end.get() else None  # 价格区间
            xlqj = [self.sales_start.get(), self.sales_end.get()]  # 销量区间
            sort = self.sort.get()  # 排序
            page_count = self.page_count.get()  # 需要获取的页数
            pd_filer = self.pd_filter.get()  # 拼单数
        except Exception as e:
            tkinter.messagebox.showinfo('输入有误', '输入有误%s' % e)
            return

        # fulter = [self.pool.submit(self.get_goods, gjz=gjz, page_count=page_count, price=jgqj, sort=sort, sales_filete=xlqj, pd_filter=pd_filer) for gjz in gjz_list]
        # wait(fulter)
        try:
            self.data_info = []
            for gjz in gjz_list:
                data = self.get_goods(gjz, page_count, jgqj, sort, xlqj, pd_filer)
                if not data:
                    tkinter.messagebox.showerror('IP', 'IP受到限制！！')
                    return
                print(json.dumps(data))
                self.data_info.append(data)
        except Exception as e:
            tkinter.messagebox.showerror('BUG', '截图给程序员：%s' % e)
            return
        tkinter.messagebox.showinfo('SUCCESS', '所有任务执行完毕！')

    def get_goods(self, gjz, page_count, price, sort, sales_filete, pd_filter):
        """
        获取指定关键字的商品
        :param gjz: String 关键字
        :param page_count:  int 需要获取多少也
        :param price: String 价格区间， 默认None代表不筛选， 否则 pricce = 'price,10,100'
        :param sort: String 排序 default综合， _credit评分， _sales销量， price价格从低到高， _price价格从高到低
        :param sales_filete: list sales_filete销量区间 [10,1000]
        :param pd_filter: int 过滤拼团数量
        :return:
        """
        headers = {
            'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
            'Host': 'apiv3.yangkeduo.com'
        }
        data = {'gjz': gjz, 'price_qj': self.get_price_qj(gjz), 'goods_list': []}

        # 开始循环获取商品
        for page in range(1, page_count + 1):
            url = 'http://apiv3.yangkeduo.com/search?q=%s&page=%s&size=50&requery=0&list_id=search_UHpDve&sort=%s' % (
                gjz, page, sort)
            if price:
                url += '&filter=%s' % price
            response = requests.get(url=url, headers=headers)
            # 所有商品的列表
            print(response.text)
            good_list = json.loads(response.text)
            if good_list.get('error_code', None):
                if good_list['error_code'] == 40001:
                    messagebox.askretrycancel('受限', 'IP受到限制，请更换IP')
                    continue
            # 开始获取商品
            for good in good_list.get('items'):
                # 商品ID
                goods_id = good['goods_id']
                # 标题链接
                link = 'http://mobile.yangkeduo.com/goods.html?goods_id=%s' % goods_id
                # 销量
                sales = good['sales']
                if sales_filete[1]:
                    if not sales_filete[0] < sales < sales_filete[1]:
                        continue
                # 价格
                t = list(str(good['normal_price']))
                t.insert(-2, '.')
                normal_price = float(''.join(t))
                if not int(price.split(',')[1]) < normal_price < int(price.split(',')[2]):
                    continue
                # 当前可拼数量, 及名称
                good_name, p_count = self.get_p_count(goods_id)
                if pd_filter != 0:
                    if p_count < pd_filter:
                        continue
                dd = [goods_id, link, good_name, p_count, sales, normal_price]
                self.info.insert('', 0, values=(goods_id, good_name, p_count, sales, normal_price))
                print(dd)
                data['goods_list'].append(dd)
        return data

    # 获取当前商品以拼数量
    def get_p_count(self, good_id):
        """
        获取指定商品的当前拼单人数，以及商品名称
        :param good_id: 商品ID
        :return: （商品名称， 拼单人数）
        """
        headers = {
            'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
        }
        response = requests.get(url='http://mobile.yangkeduo.com/goods.html?goods_id=%s' % good_id, headers=headers)
        json_find = re.findall('window.rawData=\s+(?P<n>{.+});', response.text)
        if json_find:
            data = json.loads(json_find[0])
            try:
                goods_name = data['initDataObj']['goods']['goodsName']
            except Exception as e:
                goods_name = ''
            try:
                lo = data['initDataObj']['goods']['localGroupsTotal']
            except Exception as e:
                lo = 0
            return goods_name, lo
        else:
            return '', 0

    # 获取商品价格区间
    def get_price_qj(self, gjz):
        headers = {
            'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
            'Host': 'apiv3.yangkeduo.com'
        }
        response = requests.get(url='http://apiv3.yangkeduo.com/search?q=%s' % gjz, headers=headers)
        good_list = json.loads(response.text)
        price_qj = ''
        if good_list.get('filter', None):
            for i in good_list['filter'].get('price', []):
                v = list(i.values())
                if v:
                    if v[-1] == -1:
                        price_qj += '%s以上' % v[0]
                    else:
                        price_qj += '%s-%s//' % (v[0], v[1])
        return price_qj

    # 导出数据
    def export_info(self):
        file_dir = askdirectory()
        if file_dir:
            if not self.data_info:
                messagebox.showinfo('导出成功', '当前没用数据！')
            else:
                try:
                    file_path = os.path.join(file_dir, 'result.xlsx')
                    workbook = openpyxl.Workbook()
                    worksheet = workbook.active
                    for data in self.data_info:
                        worksheet.append(['', ''])
                        worksheet.append(['关键字', '价格区间'])
                        worksheet.append([data['gjz'], data['price_qj']])
                        worksheet.append(['上家ID', '标题链接', '标题', '当前拼团人数', '销量', '价格'])
                        for good_info in data['goods_list']:
                            worksheet.append(good_info)
                    workbook.save(file_path)
                    messagebox.showinfo('SUCCESS', '导出成功,请查看:%s' % file_path)
                except Exception as e:
                    messagebox.showerror('导出数据失败', '%s' % e)


if __name__ == '__main__':
    PddSpider()
