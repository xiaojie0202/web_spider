from tkinter import ttk
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, wait
import json
import time
import requests
import tkinter
import tkinter.messagebox
import os
import openpyxl
import pygame
import win32api

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# win32api.ShellExecute(0, 'open', 'web.exe', '','',0)
# 获取指定城市发方的所有号牌类型
def get_city_type(city_code, city_id):
    """
    get_city_vehicle_type('he', '130300000400')
    获取当前城市的所有汽车类型是否发放 小型新能源汽车 号牌
    :param city_id: 城市ID
    :param city_code:  城市编码
    :return: (True, ['小型汽车'])
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    try:
        response = requests.post(url='http://%s.122.gov.cn/m/mvehxh/glbmData' % city_code, data={'glbm': city_id},
                                 headers=headers)
        print(response.text)
    except Exception as e:
        return False, '访问出错！'
    if response.status_code == 200:
        data_list = []
        hpzlList = json.loads(response.text)["data"]["hpzlList"]
        for i in hpzlList:
            data_list.append(i['value'].strip())
        return True, data_list
    else:
        return False, '访问出错！'


class MonitoringCarType(object):
    """
    监控各城市车管所是否发布 小型新能源汽车 号牌
    """

    def __init__(self):
        self.monitoring_list = []  # 需要监控的数据  {'city':'城市名称', 'city_id':'城市ID'，'city_code':'城市代码'}

        self.monitoring_task = None  # 线程任务

        self.is_stop_task = False  # 是否点击停止监控

        self.violation_list = []  # 报警的城市

        self.play_task = None  # 声音报警的任务

        self.play_stop = False  # 是否停止声音报警

        self.pool = ThreadPoolExecutor(10)

        self.root = tkinter.Tk()
        self.root_width = 500  # 窗口款多
        self.root_height = 600  # 窗口高度

        self.init_root_wind()  # 初始化主窗口信息

        # 顶部标签 30px
        tkinter.Label(self.root, text='列表包含新能源', font=('黑体', 15), fg='red').pack(side=tkinter.TOP, pady=10)

        # ________导入数据按钮， 报警设置
        self.header_frame = tkinter.Frame(self.root)
        self.header_frame.pack(fill=tkinter.X, padx=20)

        # 批量导入城市信息数据
        self.import_excex_btn = tkinter.Button(self.header_frame, text='导入数据', fg='red', width=20,
                                               command=self.import_data)
        self.import_excex_btn.pack(side=tkinter.LEFT)

        # 报警相关设置
        tkinter.Label(self.header_frame, text='报警方式:', font=('黑体', 12), fg='red').pack(side=tkinter.LEFT, padx=12)

        # 声音报警
        self.bj_voice = tkinter.IntVar()
        self.bj_voice_checkbox = ttk.Checkbutton(self.header_frame, text='声音报警', variable=self.bj_voice)
        self.bj_voice_checkbox.pack(side=tkinter.LEFT)

        # 弹窗报警
        self.bj_popup = tkinter.IntVar()
        self.bj_popup_checkbox = ttk.Checkbutton(self.header_frame, text='弹窗报警', variable=self.bj_popup)
        self.bj_popup_checkbox.pack(side=tkinter.LEFT, padx=20)

        # _______程序1路径， 程序2路径
        self.exe_path_frame = tkinter.Frame(self.root)
        self.exe_path_frame.pack(fill=tkinter.X, padx=12, pady=12)

        # 程序路径
        tkinter.Label(self.exe_path_frame, text='程序路径:', font=('黑体', 12)).pack(side=tkinter.LEFT)

        self.app1_path = tkinter.StringVar()
        self.app1_path_input = tkinter.Entry(self.exe_path_frame, textvariable=self.app1_path)
        self.app1_path_input.pack(side=tkinter.LEFT, padx=8)

        tkinter.Label(self.exe_path_frame, text='程序路径:', font=('黑体', 12)).pack(side=tkinter.LEFT)

        self.app2_path = tkinter.StringVar()
        self.app2_path_input = tkinter.Entry(self.exe_path_frame, textvariable=self.app2_path)
        self.app2_path_input.pack(side=tkinter.LEFT, padx=8)

        # ______间隔时间， 开始监控， 停止监控
        self.fooder_frame = tkinter.Frame(self.root)
        self.fooder_frame.pack(fill=tkinter.X, padx=12)

        # 间隔时间
        tkinter.Label(self.fooder_frame, text='间隔时间(s):', font=('黑体', 12)).pack(side=tkinter.LEFT)
        self.jg_time = tkinter.StringVar()
        self.jg_time_input = tkinter.Entry(self.fooder_frame, textvariable=self.jg_time, width=5)
        self.jg_time_input.pack(side=tkinter.LEFT)

        # 停止声音
        self.stop_play_btn = tkinter.Button(self.fooder_frame, text='停止声音', fg='red', width=12, command=self.stop_play)
        self.stop_play_btn.pack(side=tkinter.LEFT, padx=10)

        # 开始任务按钮
        self.start_monitoring_btn = tkinter.Button(self.fooder_frame, text='开始监控', fg='red', width=12,
                                                   command=self.start_monitoring)
        self.start_monitoring_btn.pack(side=tkinter.LEFT, padx=10)

        # 停止任务按钮
        self.stop_monitoring_btn = tkinter.Button(self.fooder_frame, text='停止监控', fg='red', width=12,
                                                  command=self.stop_monitoring_func)
        self.stop_monitoring_btn.pack(side=tkinter.LEFT)

        # __________________底部表格
        self.result_Frame = tkinter.Frame(self.root, height=2)
        self.result_Frame.pack(fill=tkinter.X, pady=20)

        # 定义中心列表区域
        self.bj_info_table = ttk.Treeview(self.result_Frame, show="headings", columns=('城市', '出现类型', '小型新能源'),
                                          height=18)
        self.vbar = ttk.Scrollbar(self.result_Frame, orient=tkinter.VERTICAL, command=self.bj_info_table.yview)
        self.bj_info_table.configure(yscrollcommand=self.vbar.set)
        self.bj_info_table.column("城市", anchor="center", width=100)
        self.bj_info_table.column("出现类型", anchor="center", width=280)
        self.bj_info_table.column("小型新能源", anchor="center", width=100)
        self.bj_info_table.heading("城市", text="城市")
        self.bj_info_table.heading("出现类型", text="出现类型")
        self.bj_info_table.heading("小型新能源", text="小型新能源")
        self.bj_info_table.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)

        self.rest_config()
        self.root.protocol('WM_DELETE_WINDOW', self.close_win)

        self.root.mainloop()

    # 初始化主窗口
    def init_root_wind(self):
        self.root.title('列表包含新能源')

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

    # 从excel文件导入数据
    def import_data(self):
        filename = os.path.join(BASE_DIR, '导入城市.xlsx')
        if os.path.isfile(filename):
            workbook = openpyxl.load_workbook(filename=filename, read_only=True)
            worksheet = workbook.active
            for row in worksheet.rows:
                data_dict = dict(
                    city=row[0].value.strip(),
                    city_id=row[1].value.strip(),
                    city_code=row[2].value.strip()
                )
                if data_dict['city_id'] in [i['city_id'] for i in self.monitoring_list]:
                    pass
                else:
                    self.monitoring_list.append(data_dict)
                    self.bj_info_table.insert('', 'end', value=(data_dict['city'], '还未开始监控', '还未开始监控！'))
            workbook.close()
            tkinter.messagebox.showinfo('导入成功！', 'EXCEL文件导入成功:%s\n 导入监控网址数量:%s' % (filename, len(self.monitoring_list)))
            print(self.monitoring_list)
        else:
            tkinter.messagebox.showerror('文件不存在', '导入城市.xlsx文件不存在”')

    # 开始监控按钮绑定事件
    def start_monitoring(self):
        if not self.monitoring_list:
            tkinter.messagebox.showinfo('没有监控', '请先导入监控城市，再进行开始监控')
            return
        if self.bj_voice.get() != 1 and self.bj_popup.get() != 1:
            tkinter.messagebox.showinfo('为选中报警！', '请选择一种包含方式点击开始!')
            return
        try:
            self.jg_time_int = int(self.jg_time.get())
        except Exception:
            tkinter.messagebox.showinfo('间隔时间！', '间隔时间输入有误，必须是数字！')
            return

        if self.app1_path.get():
            if not os.path.isfile(self.app1_path.get()):
                tkinter.messagebox.showerror('ERRO', '程序1路径不存在')
                return

        if self.app2_path.get():
            if not os.path.isfile(self.app2_path.get()):
                tkinter.messagebox.showerror('ERRO', '程序2路径不存在')
                return

        # 判断当前是否有任务执行
        if self.monitoring_task:
            if self.monitoring_task.isAlive():
                tkinter.messagebox.showerror('ERRO', '当前有监控任务正在进行，请等待任务结束，或者停止监控！')
                return
        if tkinter.messagebox.askokcancel("Start", "是否开始监控，城市实例位数量为%s?" % len(self.monitoring_list)):
            self.is_stop_task = False
            try:
                self.monitoring_task = Thread(target=self.start_monitoring_city)
                self.monitoring_task.start()
            except Exception as e:
                tkinter.messagebox.showerror('ERRO', '出现BUG:%s' % e)

    # 开始监控的的线程任务
    def start_monitoring_city(self):
        while True:
            if self.is_stop_task:
                break
            self.violation_list = []
            for _ in map(self.bj_info_table.delete, self.bj_info_table.get_children("")):
                pass
            task_list = [self.pool.submit(self.monitoring_city_task, data_dict=i) for i in self.monitoring_list]
            wait(task_list)
            print(self.violation_list)
            # 执行报警
            Thread(target=self.send_bj_msg, args=(self.violation_list,)).start()
            time.sleep(self.jg_time_int)

    def monitoring_city_task(self, data_dict):
        # 城市，出现的类型， 是否实现小型新能源
        dd_dict = {'city': data_dict['city']}
        dd, data = self.get_city_type(data_dict['city_code'], data_dict['city_id'])
        if dd:
            if '小型新能源汽车' in data:
                self.violation_list.append(dd_dict['city'])
                self.bj_info_table.insert('', 'end', value=(
                    dd_dict['city'], str(data).replace('[', '').replace(']', ''), '是'))
            else:
                self.bj_info_table.insert('', 'end', value=(
                    dd_dict['city'], str(data).replace('[', '').replace(']', ''), '否'))
        else:
            self.bj_info_table.insert('', 'end', value=(dd_dict['city'], '访问失败！', '访问失败！'))

    def get_city_type(self, city_code, city_id):
        """
        get_city_vehicle_type('he', '130300000400')
        获取当前城市的所有汽车类型是否发放 小型新能源汽车 号牌
        :param city_id: 城市ID
        :param city_code:  城市编码
        :return: (True, ['小型汽车'])
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        try:
            response = requests.post(url='http://%s.122.gov.cn/m/mvehxh/glbmData' % city_code, data={'glbm': city_id},
                                     headers=headers, timeout=10)
        except Exception as e:
            return False, '访问出错！'
        if response.status_code == 200:
            data_list = []
            hpzlList = json.loads(response.text)["data"]["hpzlList"]
            for i in hpzlList:
                data_list.append(i['value'].strip())
            return True, data_list
        else:
            return False, '访问出错！'

        # 停止监控按钮事件

    def stop_monitoring_func(self):
        self.is_stop_task = True
        tkinter.messagebox.showinfo('停止监控任务', '停止监控任务成功！')

    # 发送报警信息
    def send_bj_msg(self, violation_list):
        if not violation_list:
            return
        # 声音报警
        if self.bj_voice.get():
            if self.play_task:
                if not self.play_task.isAlive():
                    self.play_task = Thread(target=self.play)
                    self.play_task.start()
            else:
                self.play_task = Thread(target=self.play)
                self.play_task.start()
        # 弹窗报警
        if self.bj_popup.get():
            text = ''
            for data in violation_list:
                text += data
            Thread(target=tkinter.messagebox.showerror, args=('报警信息!', text)).start()

        # 执行app1
        if self.app1_path.get():
            win32api.ShellExecute(0, 'open', self.app1_path.get(), '', '', 1)

        # 执行app2
        if self.app2_path.get():
            win32api.ShellExecute(0, 'open', self.app2_path.get(), '', '', 1)


    # 声音报警播放的mp3
    def play(self):
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(BASE_DIR, 'video'))
        while True:
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(1)
            if self.play_stop:
                break
        self.play_stop = False
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    # 停止声音警报
    def stop_play(self):
        if self.play_task:
            self.play_stop = True
            tkinter.messagebox.showinfo('SUCCESS！', '停止声音警报成功！')

    def close_win(self):
        if tkinter.messagebox.askokcancel("Quit", "是否结束程序?"):
            data = dict(
                bjss=[self.bj_voice.get(), self.bj_popup.get()],
                app1_path=self.app1_path.get(),
                app2_path=self.app2_path.get(),
                jgsj=self.jg_time.get()
            )
            with open('pz.json', 'w+', encoding='utf-8') as f:
                f.write('%s' % json.dumps(data))
            self.root.destroy()

    def rest_config(self):
        try:
            if os.path.isfile('pz.json'):
                with open('pz.json', 'r', encoding='utf-8') as f:
                    data = json.loads(f.read())
                    bjss = data.get('bjss')
                    self.bj_voice.set(bjss[0])
                    self.bj_popup.set(bjss[1])
                    self.app1_path.set(data.get('app1_path'))
                    self.app2_path.set(data.get('app2_path'))
                    self.jg_time.set(data.get('jgsj'))
        except Exception as e:
            tkinter.messagebox.showerror('配置文件出现错误！', '%s,请删除配置文件解决' % e)
if __name__ == '__main__':
    # print(get_city_type('yn', '530500000400'))
    a = MonitoringCarType()
