from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
from threading import Thread
import tkinter
import openpyxl
import requests
import json
import os


class ZTGui(object):

    def __init__(self):
        self.dh_list = []  # 保存导入的单号
        self.session_value = None
        self.data_erro = []
        self.task = None  # 线程
        self.init_gui()

    def init_gui(self):
        self.root = tkinter.Tk()
        self.root_width = 500  # 窗口款多
        self.root_height = 480  # 窗口高度
        self.init_root_wind()  # 初始化主窗口信息

        self.username = tkinter.StringVar()
        tkinter.Label(self.root, textvariable=self.username, font=('黑体', 20)).pack(pady=10)
        self.username.set('未登录')

        header_frame = tkinter.Frame(self.root)
        header_frame.pack(fill=tkinter.X, padx=20)

        header_frame_2 = tkinter.Frame(self.root)
        header_frame_2.pack(fill=tkinter.X, pady=12, padx=20)

        header_frame_3 = tkinter.Frame(self.root)
        header_frame_3.pack(fill=tkinter.X, pady=12, padx=60)

        # session
        tkinter.Label(header_frame_2, text='     session:').pack(side=tkinter.LEFT)
        self.session = tkinter.StringVar()
        self.session_input = tkinter.Entry(header_frame_2, textvariable=self.session, width=40)
        self.session_input.pack(padx=12)

        # 登陆, 导入， 开始, 导出
        tkinter.Button(header_frame_3, text='登陆', command=self.login).pack(side=tkinter.LEFT)
        tkinter.Button(header_frame_3, text='导入', command=self.import_excel).pack(side=tkinter.LEFT, padx=10)
        tkinter.Button(header_frame_3, text='开始', command=self.start).pack(side=tkinter.LEFT, padx=10)
        tkinter.Button(header_frame_3, text='导出', command=self.export_info).pack(side=tkinter.LEFT)

        # 展示信息的表格
        # 商品表格的frame
        self.goods_Frame = tkinter.Frame(self.root)
        self.goods_Frame.pack(fill=tkinter.X)

        # 定义中心列表区域
        self.info = ttk.Treeview(self.goods_Frame, show="headings", columns=('单号', '状态'))
        self.vbar = ttk.Scrollbar(self.goods_Frame, orient=tkinter.VERTICAL, command=self.info.yview)
        self.info.configure(yscrollcommand=self.vbar.set)
        self.info.column("单号", anchor="center", width=280)
        self.info.column("状态", anchor="center", width=200)
        self.info.heading("单号", text="单号")
        self.info.heading("状态", text="状态")
        self.info.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)

        self.root.mainloop()

    # 初始化主窗口
    def init_root_wind(self):
        self.root.title('中天系统v2.2')

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

    def login(self):
        session = self.session.get()
        if not session:
            messagebox.showerror('SESSION', '请输入session')
        response = requests.get(url='https://pro.zt-express.com/common/getUserInfo',
                                cookies={'SESSION': session.strip()})
        try:
            self.username.set(json.loads(response.text)['result']['nodeName'])
            self.session_value = session.strip()
            messagebox.showinfo('登陆成功', '登陆成功！')
        except Exception as e:
            messagebox.showerror('登陆失败', '登陆失败，请检查session')

    # 导入excel表格
    def import_excel(self):
        excel_file = askopenfilename()
        if excel_file:
            if not os.path.isfile(excel_file):
                messagebox.showinfo('导入失败', '导入失败当前文件不存在！')
                return
            if not excel_file.endswith('xlsx'):
                messagebox.showinfo('导入失败', '导入文件应该是"xlsx"文件!')
                return
            workbook = openpyxl.load_workbook(excel_file)
            worksheet = workbook.active
            for row in worksheet.rows:
                value = row[0].value
                print(value)
                if value:
                    self.dh_list.append(value)
            # temp_list = [str(row[0].value).strip() for row in worksheet.rows if str(row[0].value)]
            if self.dh_list:
                messagebox.showinfo('导入成功', '导入成功，当前导入单号数量:  %s' % len(self.dh_list))
                print(self.dh_list)
                return
            else:
                messagebox.showinfo('导入失败', '当前文件没有数据！')
                return

    def start(self):
        if not self.session_value:
            tkinter.messagebox.showinfo('请先登陆之后再操作', '请先登陆后再操作！')
            return
        # 判断是否有任务在执行
        if self.task:
            if self.task.isAlive():
                tkinter.messagebox.showerror('ERRO', '当前有任务正在进行，请等待任务结束')
                return
        if messagebox.askyesno('开始？', '确定开始获取？'):
            self.task = Thread(target=self.inner_task)
            self.task.start()

    def inner_task(self):
        self.data_erro = []
        for dh in self.dh_list:
            self.post_dh(dh, self.session_value)

        tkinter.messagebox.showinfo('SUCCESS', '操作完毕！')

    def post_dh(self, dh, cookies):
        try:
            response = requests.post(url='https://pro.zt-express.com/billTrack/getBillTracks?billCode=%s' % dh,
                                     cookies={'SESSION': cookies})
            # {"status":true,"message":"操作成功","result":
            data = json.loads(response.text)

            json_data = {
                "billCode": str(dh),
                "reason": "送去无人，客户电话联系不上。已短信通知。",
                "sendSite": data['result']['firScanSite'],
                "sendSiteCode": data['result']['firScanSiteCode'],
                "sendSiteId": data['result']['firScanSiteId'],
                "typeCode": "A1",
                "typeName": "送无人，电话联系不上",
                "probImgs": []
            }
            # {"status":true,"message":"操作成功","result":"C0A80B4300002A9F00006666A06A39CD","statusCode":"SYS000"}
            response = requests.post(url='https://pro.zt-express.com/problem/applyProblem',
                                     cookies={'SESSION': cookies}, json=json_data)
            data = json.loads(response.text)
            print(data)
            if data['status']:
                self.info.insert('', 0, values=(dh, data['message']))
            else:
                self.data_erro.append([dh, '操作失败'])
                self.info.insert('', 0, values=(dh, '操作失败'))
        except Exception as e:
            self.data_erro.append([dh, '操作失败:%s' % e])
            self.info.insert('', 0, values=(dh, '操作失败:%s' % e))

    # 导出信息按钮事件
    def export_info(self):
        try:
            diretory = askdirectory()
            if diretory:
                erro_file = os.path.join(diretory, '%s-erro.xlsx' % self.username.get())
                erro_workbook = openpyxl.Workbook()
                erro_sheet = erro_workbook.active
                for dd in self.data_erro:
                    erro_sheet.append(dd)
                erro_workbook.save(erro_file)
                messagebox.showinfo('导出成功', '失败：%s' % erro_file)
        except Exception as e:
            messagebox.showerror('BUG', '导出文件出现BUG:%s' % e)


if __name__ == '__main__':
    # post_dh(75103089544256, '1ade8b62-fa44-4fba-8193-5ac39858addd')
    ZTGui()
