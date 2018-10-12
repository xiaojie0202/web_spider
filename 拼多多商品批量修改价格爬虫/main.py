from selenium import webdriver
from tkinter import ttk
import tkinter
import requests
import json
import os
import time
import execjs
import inspect
import ctypes
import tkinter.messagebox
import threading

WEBDRIVER = 'driver.exe'


# 获取crawlerinfo
def get_crawlerinfo():
    js = open(os.path.join(os.path.dirname(__file__), 'scsp.js'), 'r', encoding='utf-8')
    ctx = execjs.compile(js.read())
    stime = int(time.time() * 1000)
    token = "3675472405570909-%s" % stime
    crawlinfo = ctx.call('getEncode', stime, token)
    return crawlinfo


class PddUpdate(object):

    def __init__(self, cookies_dict=None):
        cookies = self.auth_cookies(cookies_dict)
        if cookies:
            self.cookies_dict = cookies
        else:
            self.cookies_dict = self.login_pdd()

        self.user_info = self.init_user_info()  # 用户信息字典
        self.username = self.user_info['username']  # 用户名
        self.mall_id = self.user_info['mall_id']  # mall_id
        self.phone = self.user_info['phone']  # 手机号
        self.dp_id = self.user_info['dp_id']  # 店铺ID
        self.goods_page_count = self.user_info['goods_page_count']  # 所有商品的页数
        self.page = 1  # 当前页码
        self.erro_update_file = '更新错误.txt'

    # 登陆拼多多获取cookies
    def login_pdd(self):
        driver = webdriver.Chrome(executable_path=WEBDRIVER)
        driver.get(url='https://mms.pinduoduo.com/Pdd.html#/login')
        print(driver.get_cookie('PASS_ID'))
        while True:
            cookies_dict = driver.get_cookie('PASS_ID')
            if cookies_dict:
                cookies_dict = {cookies_dict['name']: cookies_dict['value']}
                break
            time.sleep(1)
        driver.close()
        driver.quit()
        return cookies_dict

    # 验证cookies是否有效
    def auth_cookies(self, cookies_dict):
        # {"error_code":43001,"error_msg":"会话已过期"}
        # {"success":true,"errorCode":1000000,
        response = requests.post(url='https://mms.pinduoduo.com/earth/api/user/userinfo', cookies=cookies_dict)
        response_json = json.loads(response.text)
        if not response_json.get('success', False):
            return False
        else:
            return cookies_dict

    # 获取页数（当前用户有多少页商品）
    def get_page_count(self, mall_id):
        """
        获取当前用户有多少页数
        :param cookies_dict:
        :param mall_id:
        :return: int 页数
        """
        good_response = requests.post(url='https://mms.pinduoduo.com/vodka/v2/mms/query/display/mall/goodsList',
                                      json={"order_by": "id:desc", "size": 15, "page": 1, "mall_id": mall_id},
                                      cookies=self.cookies_dict)
        good_list_dict = json.loads(good_response.text)
        a, b = divmod(good_list_dict["result"]["total"], 15)
        if bool(b):
            return a + 1
        else:
            return a

    # 初始化用户信息
    def init_user_info(self):
        """
        :return: {'usernmae':xx, 'mall_id':xx, pahone:xx, cookies:xx, goods_page_count, 'dp_id':''}
        """
        response = requests.post(url='https://mms.pinduoduo.com/earth/api/user/userinfo', cookies=self.cookies_dict)
        user_json = json.loads(response.text)
        user_info_dict = {'username': user_json["result"]["mall"]["username"],
                          'mall_id': user_json["result"]["mall_id"],
                          'phone': user_json["result"]["mobile"], 'cookies': self.cookies_dict,
                          'goods_page_count': self.get_page_count(user_json["result"]["mall_id"]),
                          'dp_id': user_json["result"]['id']}
        info = '''
            [x]用户名：%s
            [x]手机号:%s
            [x]商品页:%s页
        ''' % (
            user_json["result"]["username"], user_json["result"]["mobile"],
            user_info_dict['goods_page_count'])
        print(info)
        return user_info_dict

    # 获取执行页面的所有商品
    def get_good_list(self, page):
        """
        获取当前页面的商品
        :param page: 页数
        :return: [{'id':155255, "goods_name": '商品名称'},{。。。}]
        """
        dd = []
        good_response = requests.post(url='https://mms.pinduoduo.com/vodka/v2/mms/query/display/mall/goodsList',
                                      json={"order_by": "id:desc", "size": 15, "page": page, "mall_id": self.mall_id},
                                      cookies=self.cookies_dict)
        good_list_dict = json.loads(good_response.text)
        # {"error_code":43001,"error_msg":"会话已过期"}
        print(good_list_dict)
        if good_list_dict.get('error_code', 12) == 43001:
            return False
        # 总共商品数量
        # good_list_dict["result"]["total"]
        # 所有商品组成的list
        # good_list_dict["result"]["goods_list"]
        for i in good_list_dict["result"]["goods_list"]:
            dd.append({'id': i["id"], 'goods_name': i['goods_name']})
        return dd

    # 获取需要编辑商品的goods_commit_id（草稿）, 传入商品ID（）
    def get_goods_commit_id(self, goods_id):
        """
        创建需要编辑商品的草稿，并返回草稿ID
        :param goods_id: 商品ID
        :return: 草稿ID
        """
        a = requests.post(url='https://mms.pinduoduo.com/glide/v2/mms/edit/commit/create_by_sn',
                          json={"goods_id": goods_id},
                          cookies=self.cookies_dict)
        # {"success":true,"error_code":1000000,"error_msg":null,"result":{"goods_commit_id":5254260830}}
        # {"success":false,"error_code":900009,"error_msg":"商品禁售中，不可编辑，请联系商家支持","result":null}
        # {"success":true,"error_code":1000000,"error_msg":null,"result":{"goods_commit_id":5512839905}}
        info = json.loads(a.text)
        if info['success']:
            goods_commit_id = info['result']['goods_commit_id']
            return True, goods_commit_id
        else:
            return False, info['error_msg']

    # 获取需要编辑商品的信息, 传入商品的草稿ID
    def get_goods_edit_info(self, goods_commit_id):
        b = requests.get(url='https://mms.pinduoduo.com/glide/v2/mms/query/commit/detail/%s' % goods_commit_id,
                         cookies=self.cookies_dict)
        return json.loads(b.text)['result']

    # 拼接更新信息
    def margen_post_date(self, edit_json, operator_dict):
        """
        :param edit_json: 获取的编辑商品的详细信息
                                市场价[运算，数值]， 团购价【运算，数值】，单价【运算，数值】
        :param operator_dict: {'market_price': ['*', '1.3'], 'multi_price': ['*', '1.3'], 'price':['*', '1.3']}
        :return: json
        """
        commmit_dict = {
            "goods_id": edit_json["goods_id"],
            "goods_commit_id": str(edit_json["id"]),
            "goods_commit_check": edit_json["goods_commit_check"],
            "reject_reason": edit_json["reject_reason"],
            "reject_status": edit_json["reject_status"],
            "check_status": edit_json["check_status"],
            "tiny_name": edit_json["tiny_name"],
            "goods_name": edit_json["goods_name"],
            "video_url": "",
            "goods_desc": edit_json["goods_desc"],
            "warm_tips": edit_json["warm_tips"],
            "cat_id": edit_json["cat_id"],
            "cats": edit_json["cats"],
            "image_url": edit_json["image_url"],
            "fabric": edit_json["fabric"],  # ""空字符串
            "fabric_content": edit_json["fabric_content"],  # 空字符串
            "paper_length": edit_json["paper_length"],  # 字符串
            "paper_net_weight": edit_json["paper_net_weight"],
            "paper_plies_num": edit_json["paper_plies_num"],
            "paper_width": edit_json["paper_width"],
            "shelf_life": "",  # edit_json["commit_extension"]["shelf_life"]
            "start_production_date": "",  # edit_json["commit_extension"]["start_production_date"]
            "end_production_date": "",  # edit_json["commit_extension"]["end_production_date"]
            "production_license": "",  # "production_license"
            "production_standard_number": "",  # "production_standard_number"
            "is_draft": edit_json["is_draft"],
            "cat_ids": edit_json["cat_ids"],
            "id": "",
            "out_goods_sn": edit_json["commit_extension"]["out_goods_sn"],
            "created_at": edit_json["commit_extension"]["created_at"],
            "updated_at": edit_json["commit_extension"]["updated_at"],
            "is_shop": edit_json["is_shop"],
            "goods_type": edit_json["goods_type"],
            "invoice_status": edit_json["invoice_status"],
            "zhi_huan_bu_xiu": edit_json["zhi_huan_bu_xiu"],
            "quan_guo_lian_bao": edit_json["quan_guo_lian_bao"],
            "second_hand": edit_json["second_hand"],
            "is_pre_sale": edit_json["is_pre_sale"],
            "pre_sale_time": edit_json["pre_sale_time"],
            "country": edit_json["country"],
            "country_id": edit_json["country_id"],
            "warehouse": edit_json["warehouse"],
            "customs": edit_json["customs"],
            "is_customs": edit_json["is_customs"],
            "shipment_limit_second": edit_json["shipment_limit_second"],
            "cost_template_id": edit_json["cost_template_id"],
            "weight": 1,
            "groups": edit_json["groups"],
            "is_folt": edit_json["is_folt"],
            "is_refundable": edit_json["is_refundable"],
            "elec_goods_attributes": edit_json["elec_goods_attributes"],
            "market_price": edit_json["market_price"],  # 市场价
            "gallery": [],
            "goods_properties": [],
            "is_auto_save": False,
            "skus": []
        }
        if operator_dict['market_price'][1] not in ['0', '0.0']:
            commmit_dict["market_price"] = int(eval("%s%s%s" % (
                commmit_dict["market_price"], operator_dict['market_price'][0], operator_dict['market_price'][1])))
        # 设置commit——dict的 gallery
        for i in edit_json["galleries"]:
            commmit_dict["gallery"].append({"url": i["url"], "type": i["type"]})

        for sku in edit_json["sku"]:
            a = {
                'id': sku['id'],
                "limit_quantity": sku["limit_quantity"],
                "out_sku_sn": sku["out_sku_sn"],
                "is_onsale": sku["is_onsale"],
                "thumb_url": sku["thumb_url"],
                "quantity_delta": sku["quantity_delta"],
                "multi_price": sku["multi_price"],
                "price": sku["price"],
                "weight": sku["weight"],
                "spec": sku["spec"]
            }
            if operator_dict['multi_price'][1] not in ['0', '0.0']:
                a["multi_price"] = int(
                    eval('%s%s%s' % (
                        a["multi_price"], operator_dict['multi_price'][0], operator_dict['multi_price'][1])))
            if operator_dict["price"][1] not in ['0', '0.0']:
                a["price"] = int(eval('%s%s%s' % (a["price"], operator_dict['price'][0], operator_dict['price'][1])))
            commmit_dict["skus"].append(a)

        return commmit_dict

    # 更新商品信息到草稿
    def update_edit_goods(self, goods_json):
        """
        更新修改的商品信息到草稿
        # {"success":true,"error_code":1000000,"error_msg":null,"result":true}
        :param goods_json: 拼接的商品更新信息
        :return:
        """
        response = requests.post(url='https://mms.pinduoduo.com/glide/v2/mms/edit/commit/update', json=goods_json,
                                 cookies=self.cookies_dict)
        #
        response_json = json.loads(response.text)
        if response_json.get('error_code', 12) != 1000000:
            return False, response_json['error_msg']
        else:
            return True, ''

    # 提交草稿更新到数据库
    def commit_edit_goods(self, goods_commit_id, crawlerinfo):
        cg = requests.post(url='https://mms.pinduoduo.com/glide/v2/mms/edit/commit/submit', cookies=self.cookies_dict,
                           json={"goods_commit_id": goods_commit_id, "is_onsale": False,
                                 "crawlerInfo": crawlerinfo}
                           )
        # 提交草稿 {"success":false,"error_code":100002,"error_msg":"箱包分类因分类调整已失效，请返回重新选择分类","result":null}
        response_json = json.loads(cg.text)
        if response_json.get('error_code', 12) != 1000000:
            try:
                return False, response_json['error_msg']
            except Exception:
                return False, response_json
        else:
            return True, '价格更新成功！'

    # 更新一页商品
    def update_page_goods(self, page, operator_dict):
        """
        更新一页商品
        :return:
        """
        erro_update = []  # 更新失败的商品 {id：xx 商品名称:xx， erromsg: xx}
        seccess_update = []  # 更新成功的商品

        good_list = self.get_good_list(page)
        for good in good_list:  # {'id':155255, "goods_name": '商品名称'}
            time.sleep(8)
            # 获取草稿ID
            info, goods_commit_id = self.get_goods_commit_id(good['id'])
            if not info:
                erro = good
                erro['erromsg'] = goods_commit_id
                erro_update.append(erro)
                print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good['goods_name'], goods_commit_id))
                continue
            edit_json = self.get_goods_edit_info(goods_commit_id)

            # 拼接完毕需要编辑的商品信息
            goods_json = self.margen_post_date(edit_json, operator_dict)
            # 提交到草稿
            result, erromsg = self.update_edit_goods(goods_json)
            if not result:
                erro = good
                erro['erromsg'] = erromsg
                erro_update.append(erro)
                print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good['goods_name'], erromsg))
                continue
            # 提交到数据库
            result, erromsg = self.commit_edit_goods(goods_commit_id, get_crawlerinfo())
            if not result:
                erro = good
                erro['erromsg'] = erromsg
                erro_update.append(erro)
                print('[EERO]%s-->更新到数据库失败错误信息:[%s]' % (good['goods_name'], erromsg))
                continue
            print('[SUCCESS]%s-->价格更新成功' % good['goods_name'])
            erro = good
            erro['erromsg'] = '[SUCCESS]更新成功'
            seccess_update.append(erro)
        # 错误信息保存到文件
        with open(self.erro_update_file, 'a+', encoding='utf-8') as f:
            for i in erro_update:
                a = '店铺ID:%s----商品ID:%s----商品名称:%s----错误信息:%s\n' % (self.dp_id, i['id'], i['goods_name'], i['erromsg'])
                f.write(a)
        return erro_update + seccess_update


class PddGUI(object):

    def __init__(self):
        self.userinfo_file = 'userinfo.pdd'
        self.login_user_dict = {}  # 保存当前登陆的用户
        self.select_user_key = None  # 当前选中的用户
        self.thread_task = {}  # 存放每个账号执行的多任务的线程 {‘key’: 线程对象}

        self.root = tkinter.Tk()
        self.root_width = 800  # 窗口款多
        self.root_height = 800  # 窗口高度

        self.init_root_wind()  # 初始化主窗口信息

        # 顶部标签 30px
        tkinter.Label(self.root, text='拼多多商品批量修改价格', font=('黑体', 20), fg='red').pack(side=tkinter.TOP, pady=10)

        # -----------------------------------------顶部的frame
        # 用户相关的Framew
        self.user_Frame = tkinter.Frame(self.root, height=120)
        self.user_Frame.pack(fill=tkinter.X)

        # 显示登陆用户的listbox
        self.login_user_listbox = tkinter.Listbox(self.user_Frame, selectmode=tkinter.BROWSE)
        self.login_user_listbox.pack(fill=tkinter.Y, side=tkinter.LEFT, padx=10)
        self.init_user_listbox()  # 初始化登陆用户框
        self.login_user_listbox.bind("<Double-Button-1>", self.login_user_listbox_click)  # 绑定listbox双击事件

        # 显示当前选中的用户
        self.show_user_name_label = tkinter.Label(self.user_Frame, text='当前没有选中用户', font=('黑体', 12), fg='red')
        self.show_user_name_label.pack(fill=tkinter.Y, side=tkinter.LEFT, padx=100)

        # 登陆用户和退出用户
        self.login_user_btn = tkinter.Button(self.user_Frame, text='登陆新用户', fg='red', width=20,
                                             command=self.login_new_user)
        self.login_user_btn.pack(side=tkinter.LEFT, padx=10)

        self.logout_user_btn = tkinter.Button(self.user_Frame, text='登出', fg='red', width=20, command=self.logout_user)
        self.logout_user_btn.pack(side=tkinter.LEFT, padx=10)
        # --------------------------------------

        # ------------------------------- 中上， 上一页，下一页， 跳转到指定页面按钮
        # 三个按钮的frame
        self.page_frame = tkinter.Frame(self.root, height=40)
        self.page_frame.pack(fill=tkinter.X, pady=5)
        # 上一页按钮
        self.pre_page = tkinter.Button(self.page_frame, text='上一页', command=self.pre_page_func)
        self.pre_page.pack(side=tkinter.LEFT, padx=120)

        # 跳转到指定页面的输入框
        self.page_number = tkinter.IntVar()
        self.page_input = tkinter.Entry(self.page_frame, textvariable=self.page_number)
        self.page_input.pack(side=tkinter.LEFT)
        # 跳转按钮
        self.spick = tkinter.Button(self.page_frame, text='跳转', command=self.spick_page_func)
        self.spick.pack(side=tkinter.LEFT)

        # 下一页按钮
        self.next_page = tkinter.Button(self.page_frame, text='下一页', command=self.next_page_func)
        self.next_page.pack(side=tkinter.LEFT, padx=120)
        # ---------------------------------------------------------

        # ------------------显示商品信息的表格
        # 商品表格的frame
        self.goods_Frame = tkinter.Frame(self.root, height=320)
        self.goods_Frame.pack(fill=tkinter.X)

        # 定义中心列表区域
        self.goods_list_table = ttk.Treeview(self.goods_Frame, show="headings", columns=('商品ID', '商品名称', '更新信息'))
        self.vbar = ttk.Scrollbar(self.goods_Frame, orient=tkinter.VERTICAL, command=self.goods_list_table.yview)
        self.goods_list_table.configure(yscrollcommand=self.vbar.set)
        self.goods_list_table.column("商品ID", anchor="center", width=100)
        self.goods_list_table.column("商品名称", anchor="center", width=380)
        self.goods_list_table.column("更新信息", anchor="center", width=300)
        self.goods_list_table.heading("商品ID", text="商品ID")
        self.goods_list_table.heading("商品名称", text="商品名称")
        self.goods_list_table.heading("更新信息", text="更新信息")
        self.goods_list_table.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar.grid(row=0, column=1, sticky=tkinter.NS)
        # ------------修改价格的一堆标签------------------

        # 修改商品价格frame
        self.update_price_Frame = tkinter.Frame(self.root)
        self.update_price_Frame.pack(fill=tkinter.X, padx=70, pady=10)

        # 市场价标签
        tkinter.Label(self.update_price_Frame, text='市场价:', font=('黑体', 20)).pack(side=tkinter.LEFT)
        # 市场价的下拉框
        self.scj_ys_selsect = ttk.Combobox(self.update_price_Frame, width=5)
        self.scj_ys_selsect.pack(side=tkinter.LEFT, padx=2)
        self.scj_ys_selsect["values"] = ("+", "-", "*", "/")
        self.scj_ys_selsect["state"] = "readonly"
        self.scj_ys_selsect.current(0)
        # 市场价的输入框
        self.scj_value = tkinter.StringVar()
        self.scj_input = tkinter.Entry(self.update_price_Frame, textvariable=self.scj_value, width=5)
        self.scj_input.pack(side=tkinter.LEFT)
        self.scj_value.set('0')

        # 团购价标签
        tkinter.Label(self.update_price_Frame, text='团购价:', font=('黑体', 20)).pack(side=tkinter.LEFT)
        # 团购价的下拉框
        self.tgj_ys_selsect = ttk.Combobox(self.update_price_Frame, width=5)
        self.tgj_ys_selsect.pack(side=tkinter.LEFT, padx=2)
        self.tgj_ys_selsect["values"] = ("+", "-", "*", "/")
        self.tgj_ys_selsect["state"] = "readonly"
        self.tgj_ys_selsect.current(0)
        # 团购价输入框
        self.tgj_value = tkinter.StringVar()
        self.tgj_input = tkinter.Entry(self.update_price_Frame, textvariable=self.tgj_value, width=5)
        self.tgj_input.pack(side=tkinter.LEFT)
        self.tgj_value.set('0')

        # 单买价
        tkinter.Label(self.update_price_Frame, text='单买价:', font=('黑体', 20)).pack(side=tkinter.LEFT)
        # 单买价的下拉框
        self.dmj_ys_selsect = ttk.Combobox(self.update_price_Frame, width=5)
        self.dmj_ys_selsect.pack(side=tkinter.LEFT, padx=2)
        self.dmj_ys_selsect["values"] = ("+", "-", "*", "/")
        self.dmj_ys_selsect["state"] = "readonly"
        self.dmj_ys_selsect.current(0)
        # 单买价输入框
        self.dmj_value = tkinter.StringVar()
        self.dmj_input = tkinter.Entry(self.update_price_Frame, textvariable=self.dmj_value, width=5)
        self.dmj_input.pack(side=tkinter.LEFT)
        self.dmj_value.set('0')

        # ----------------------------------------更新多页商品价格
        self.fooder_btn_frame = tkinter.Frame(self.root)
        self.fooder_btn_frame.pack(fill=tkinter.X, padx=100)
        ## 更新按钮
        self.update_btn = tkinter.Button(self.fooder_btn_frame, text='更新当前页价格', fg='red',
                                         command=self.update_page_goods_2)
        self.update_btn.pack(side=tkinter.LEFT, padx=20)
        # 起始页输入框
        self.start_page_value = tkinter.StringVar()
        self.start_page_input = tkinter.Entry(self.fooder_btn_frame, textvariable=self.start_page_value, width=5)
        self.start_page_input.pack(side=tkinter.LEFT)
        self.start_page_value.set('0')

        # 起始输入框和结束输入框中间的-
        tkinter.Label(self.fooder_btn_frame, text='--', font=('黑体', 20)).pack(side=tkinter.LEFT)

        # 结束页输入框
        self.end_page_value = tkinter.StringVar()
        self.end_page_input = tkinter.Entry(self.fooder_btn_frame, textvariable=self.end_page_value, width=5)
        self.end_page_input.pack(side=tkinter.LEFT)
        self.end_page_value.set('0')

        # 更新多页价格
        self.update_mult_btn = tkinter.Button(self.fooder_btn_frame, text='开始更新多页价格', fg='red',
                                              command=self.update_mult_page_goods)
        self.update_mult_btn.pack(side=tkinter.LEFT, padx=20)

        # 停止更新多页价格
        self.stop_btn = tkinter.Button(self.fooder_btn_frame, text='停止更新多页价格', fg='red', command=self.stop_update_task)
        self.stop_btn.pack(side=tkinter.LEFT, padx=20)

        # ————————————————V2.0 版本新加功能， 更加商品ID更新商品
        self.new_v2_frame = tkinter.Frame(self.root)
        self.new_v2_frame.pack(fill=tkinter.X, padx=60, pady=10)

        tkinter.Label(self.new_v2_frame, text='商品ID:', font=('黑体', 16)).pack(side=tkinter.LEFT)

        # 商品ID 的输入框
        self.goods_id_text_frame = tkinter.Frame(self.new_v2_frame)
        self.goods_id_text_frame.pack(side=tkinter.LEFT, padx=10)

        self.impot_goods_text = tkinter.Text(self.goods_id_text_frame, width=60, height=12)
        self.vbar2 = ttk.Scrollbar(self.goods_id_text_frame, orient=tkinter.VERTICAL,
                                   command=self.impot_goods_text.yview)
        self.impot_goods_text.configure(yscrollcommand=self.vbar2.set)
        self.impot_goods_text.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.vbar2.grid(row=0, column=1, sticky=tkinter.NS)

        # 更新输入框的商品按钮
        self.update_goods_id_btn = tkinter.Button(self.new_v2_frame, text='根据商品ID更新', fg='red',
                                                  command=self.update_goods_id_func)
        self.update_goods_id_btn.pack(side=tkinter.LEFT)

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

    # 验证用户信息是否有效
    def auth_user(self, user_info):
        """
        验证用户信息是否有效
        :param user_info: {'usernmae':xx, 'mall_id':xx, pahone:xx, cookies:xx, goods_page_count, 'dp_id':''}
        :return:
        """
        response = requests.post(url='https://mms.pinduoduo.com/earth/api/user/userinfo', cookies=user_info['cookies'])
        response_json = json.loads(response.text)
        if not response_json.get('success', False):
            return False
        else:
            return user_info

    # 初始化登陆用户的listbox
    def init_user_listbox(self):
        if os.path.isfile(self.userinfo_file):
            with open(self.userinfo_file, 'r') as f:
                for user in f.readlines():
                    user_json = json.loads(user.strip())
                    if self.auth_user(user_json):
                        key = '%s-%s-%s页' % (user_json['username'], user_json['dp_id'], user_json['goods_page_count'])
                        self.select_user_key = key
                        self.login_user_listbox.insert(tkinter.END, key)
                        self.login_user_dict[key] = PddUpdate(user_json['cookies'])
        else:
            pass

    # login_user_listbox 的点击事件
    def login_user_listbox_click(self, event):
        for _ in map(self.goods_list_table.delete, self.goods_list_table.get_children("")):
            pass
        key = self.login_user_listbox.get(first=self.login_user_listbox.curselection()[0])
        try:
            user_obj = self.login_user_dict[key]
            label_text = '''用户名:%s\n总页数:%s\n当前页:%s''' % (user_obj.username, user_obj.goods_page_count, user_obj.page)
            self.show_user_name_label.config(text=label_text)  # 设置标签显示当前选中的用户
            #  获取当前用户的商品并插入到self.goods_list_table
            for i in user_obj.get_good_list(user_obj.page):
                self.goods_list_table.insert("", "end", values=(i['id'], i['goods_name'], '未更新'))
            self.select_user_key = key
        except KeyError:
            self.login_user_dict.pop(key)
            if self.select_user_key == key:
                self.select_user_key = self.login_user_dict[list(self.login_user_dict.keys())[0]]
            tkinter.messagebox.showerror(title='账号失效', message='当前账号登陆超时，请重新登陆')
            self.login_user_listbox.delete(first=self.login_user_listbox.curselection()[0])

    # 登陆新用户的按钮的点击事件
    def login_new_user(self):
        user_obj = PddUpdate()
        user_json = user_obj.user_info
        key = '%s-%s-%s页' % (user_json['username'], user_json['dp_id'], user_json['goods_page_count'])
        self.login_user_dict[key] = user_obj
        self.login_user_listbox.insert(tkinter.END, key)
        self.save_userinfo()

    # 保存当前用户信息到文件
    def save_userinfo(self):
        with open(self.userinfo_file, 'w+') as f:
            for k, v in self.login_user_dict.items():
                f.write('%s\n' % json.dumps(v.user_info))

    # 登出用户
    def logout_user(self):
        key = self.login_user_listbox.get(first=self.login_user_listbox.curselection()[0])
        if self.select_user_key == key:
            self.select_user_key = self.login_user_dict[list(self.login_user_dict.keys())[0]]
        self.login_user_dict.pop(key)
        self.login_user_listbox.delete(first=self.login_user_listbox.curselection()[0])
        self.save_userinfo()

    # 上一页按钮
    def pre_page_func(self):
        if not self.select_user_key:
            tkinter.messagebox.showinfo('erro', '当前未选中用户')
        else:
            user_obj = self.login_user_dict[self.select_user_key]
            if user_obj.page <= 1:
                tkinter.messagebox.showinfo('erro', '当前以及是第一页')
            else:
                user_obj.page -= 1
                for _ in map(self.goods_list_table.delete, self.goods_list_table.get_children("")):
                    pass
                for i in user_obj.get_good_list(user_obj.page):
                    self.goods_list_table.insert("", "end", values=(i['id'], i['goods_name'], '未更新'))

    # 下一页按钮绑定事件
    def next_page_func(self):
        if not self.select_user_key:
            tkinter.messagebox.showinfo('erro', '当前未选中用户')
        else:
            user_obj = self.login_user_dict[self.select_user_key]
            if user_obj.page >= user_obj.goods_page_count:
                tkinter.messagebox.showinfo('erro', '当前已经是最后一页！')
            else:
                user_obj.page += 1
                for _ in map(self.goods_list_table.delete, self.goods_list_table.get_children("")):
                    pass
                for i in user_obj.get_good_list(user_obj.page):
                    self.goods_list_table.insert("", "end", values=(i['id'], i['goods_name'], '未更新'))

    # 跳转到指定页面
    def spick_page_func(self):
        if not self.select_user_key:
            tkinter.messagebox.showinfo('erro', '当前未选中用户')
        else:
            try:
                paage_number = int(self.page_number.get())
                user_obj = self.login_user_dict[self.select_user_key]
                if paage_number < 1 or paage_number > user_obj.goods_page_count:
                    tkinter.messagebox.showinfo('erro', '未找到当前页面')
                else:
                    user_obj.page = paage_number
                    for _ in map(self.goods_list_table.delete, self.goods_list_table.get_children("")):
                        pass
                    for i in user_obj.get_good_list(user_obj.page):
                        self.goods_list_table.insert("", "end", values=(i['id'], i['goods_name'], '未更新'))
            except Exception as e:
                tkinter.messagebox.showerror('erro', '%s' % e)

    # 更新当前页面的商品
    def update_page_goods_2(self):
        try:
            market_price = [self.scj_ys_selsect.get(), str(float(self.scj_value.get()))]
            multi_price = [self.tgj_ys_selsect.get(), str(float(self.tgj_value.get()))]
            price = [self.dmj_ys_selsect.get(), str(float(self.dmj_value.get()))]
            operator_dict = {'market_price': market_price, 'multi_price': multi_price, 'price': price}
            if self.dmj_value.get() == '0' and self.tgj_value.get() == '0' and self.scj_value.get() == '0':
                return
            for _ in map(self.goods_list_table.delete, self.goods_list_table.get_children("")):
                pass

            user_obj = self.login_user_dict[self.select_user_key]
            good_list = user_obj.get_good_list(user_obj.page)
            erro_update = []
            for good in good_list:
                time.sleep(10)
                # 获取草稿ID
                info, goods_commit_id = user_obj.get_goods_commit_id(good['id'])
                if not info:
                    erro = good
                    erro['erromsg'] = goods_commit_id
                    erro_update.append(erro)
                    print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good['goods_name'], goods_commit_id))
                    self.goods_list_table.insert("", "end", values=(erro['id'], erro['goods_name'], erro['erromsg']))
                    self.goods_list_table.update()
                    continue
                edit_json = user_obj.get_goods_edit_info(goods_commit_id)

                # 拼接完毕需要编辑的商品信息
                goods_json = user_obj.margen_post_date(edit_json, operator_dict)
                # 提交到草稿
                result, erromsg = user_obj.update_edit_goods(goods_json)

                if not result:
                    erro = good
                    erro['erromsg'] = erromsg
                    erro_update.append(erro)
                    print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good['goods_name'], erromsg))
                    self.goods_list_table.insert("", "end", values=(erro['id'], erro['goods_name'], erro['erromsg']))
                    self.goods_list_table.update()
                    continue
                # 提交到数据库
                result, erromsg = user_obj.commit_edit_goods(goods_commit_id, get_crawlerinfo())
                if not result:
                    erro = good
                    erro['erromsg'] = erromsg
                    erro_update.append(erro)
                    print('[EERO]%s-->更新到数据库失败错误信息:[%s]' % (good['goods_name'], erromsg))
                    self.goods_list_table.insert("", "end", values=(erro['id'], erro['goods_name'], erro['erromsg']))
                    self.goods_list_table.update()
                    continue
                print('[SUCCESS]%s-->价格更新成功' % good['goods_name'])
                erro = good
                erro['erromsg'] = '[SUCCESS]更新成功'
                self.goods_list_table.insert("", "end", values=(erro['id'], erro['goods_name'], erro['erromsg']))
                self.goods_list_table.update()
            with open(user_obj.erro_update_file, 'a+', encoding='utf-8') as f:
                for i in erro_update:
                    a = '店铺ID:%s----商品ID:%s----商品名称:%s----错误信息:%s\n' % (
                        user_obj.dp_id, i['id'], i['goods_name'], i['erromsg'])
                    f.write(a)
            print(operator_dict)
        except Exception as e:
            tkinter.messagebox.showerror('输入有误', '%s' % e)

    # 更新多页商品价格按钮绑定事件
    def update_mult_page_goods(self):
        try:
            market_price = [self.scj_ys_selsect.get(), str(float(self.scj_value.get()))]
            multi_price = [self.tgj_ys_selsect.get(), str(float(self.tgj_value.get()))]
            price = [self.dmj_ys_selsect.get(), str(float(self.dmj_value.get()))]
            operator_dict = {'market_price': market_price, 'multi_price': multi_price, 'price': price}
            if self.dmj_value.get() == '0' and self.tgj_value.get() == '0' and self.scj_value.get() == '0':
                return

            user_obj = self.login_user_dict[self.select_user_key]
            start_page_value = int(self.start_page_value.get())
            end_page_value = int(self.end_page_value.get())
            if start_page_value < 0 or end_page_value > user_obj.goods_page_count or start_page_value > end_page_value:
                tkinter.messagebox.showerror('输入有误', '页面范围输入有误！')
                return
            else:
                if self.thread_task.get(self.select_user_key, None):
                    if self.thread_task[self.select_user_key].isAlive():
                        tkinter.messagebox.showinfo('当前用户有任务执行', '当前用户有任务执行！， 无法添加新任务')
                        return
                # 创建多线程进行更新
                self.thread_task[self.select_user_key] = threading.Thread(target=self.update_dpage_goods_task, args=(
                    user_obj, start_page_value, end_page_value, operator_dict,))
                self.thread_task[self.select_user_key].start()

        except Exception as e:
            tkinter.messagebox.showerror('输入有误', '%s' % e)

    # 更新多页商品任务
    def update_dpage_goods_task(self, user_obj, start, end, operator_dict):
        # 清空table
        for _ in map(self.goods_list_table.delete, self.goods_list_table.get_children("")):
            pass
        erro_update = []
        for page in range(start, end + 1):
            # 更新标签显示的用户信息，以及当前页数
            user_obj.page = page
            label_text = '''用户名:%s\n总页数:%s\n当前页:%s''' % (user_obj.username, user_obj.goods_page_count, user_obj.page)
            self.show_user_name_label.config(text=label_text)
            good_list = user_obj.get_good_list(page)
            if not good_list:
                tkinter.messagebox.showerror('错误', '当前用户会话过期，需要重新登陆！')
                return
            try:
                for good in good_list:
                    print('当前操作商品', good)
                    time.sleep(10)
                    # 获取草稿ID
                    info, goods_commit_id = user_obj.get_goods_commit_id(good['id'])
                    if not info:
                        erro = good
                        erro['erromsg'] = goods_commit_id
                        erro_update.append(erro)
                        print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good['goods_name'], goods_commit_id))
                        self.goods_list_table.insert("", "end",
                                                     values=(erro['id'], erro['goods_name'], erro['erromsg']))
                        self.goods_list_table.update()
                        continue
                    print('goods_commit_id', goods_commit_id)
                    edit_json = user_obj.get_goods_edit_info(goods_commit_id)
                    print('edit_json', edit_json)
                    # 拼接完毕需要编辑的商品信息
                    goods_json = user_obj.margen_post_date(edit_json, operator_dict)
                    print('goods_json', goods_json)
                    # 提交到草稿
                    result, erromsg = user_obj.update_edit_goods(goods_json)
                    print(result, erromsg)

                    if not result:
                        erro = good
                        erro['erromsg'] = erromsg
                        erro_update.append(erro)
                        print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good['goods_name'], erromsg))
                        self.goods_list_table.insert("", "end",
                                                     values=(erro['id'], erro['goods_name'], erro['erromsg']))
                        self.goods_list_table.update()
                        continue
                    # 提交到数据库
                    result, erromsg = user_obj.commit_edit_goods(goods_commit_id, get_crawlerinfo())
                    if not result:
                        erro = good
                        erro['erromsg'] = erromsg
                        erro_update.append(erro)
                        print('[EERO]%s-->更新到数据库失败错误信息:[%s]' % (good['goods_name'], erromsg))
                        self.goods_list_table.insert("", "end",
                                                     values=(erro['id'], erro['goods_name'], erro['erromsg']))
                        self.goods_list_table.update()
                        continue
                    print('[SUCCESS]%s-->价格更新成功' % good['goods_name'])
                    erro = good
                    erro['erromsg'] = '[SUCCESS]更新成功'
                    self.goods_list_table.insert("", "end", values=(erro['id'], erro['goods_name'], erro['erromsg']))
                    self.goods_list_table.update()
            except Exception as e:
                print(e)
                tkinter.messagebox.showerror('错误', '当前商品更新失败！%s' % e)

            with open(user_obj.erro_update_file, 'a+', encoding='utf-8') as f:
                for i in erro_update:
                    a = '店铺ID:%s----商品ID:%s----商品名称:%s----错误信息:%s\n' % (
                        user_obj.dp_id, i['id'], i['goods_name'], i['erromsg'])
                    f.write(a)
            print(operator_dict)
        tkinter.messagebox.showinfo('SUCCESS', '%s用户更新%s-%s页商品价格完毕' % (user_obj.username, start, end))

    # 根据商品ID 进行更新商品
    def update_goods_id_func(self):
        try:
            market_price = [self.scj_ys_selsect.get(), str(float(self.scj_value.get()))]
            multi_price = [self.tgj_ys_selsect.get(), str(float(self.tgj_value.get()))]
            price = [self.dmj_ys_selsect.get(), str(float(self.dmj_value.get()))]
            operator_dict = {'market_price': market_price, 'multi_price': multi_price, 'price': price}
            if self.dmj_value.get() == '0' and self.tgj_value.get() == '0' and self.scj_value.get() == '0':
                tkinter.messagebox.showinfo('警告', '未输入价格更新情况！')
                return
            if not self.select_user_key:
                tkinter.messagebox.showinfo('未现在用户', '请先选择用户再进行操作!')
                return

            user_obj = self.login_user_dict[self.select_user_key]

            if self.thread_task.get(self.select_user_key, None):
                if self.thread_task[self.select_user_key].isAlive():
                    tkinter.messagebox.showinfo('当前用户有任务执行', '当前用户有任务执行！， 无法添加新任务')
                    return

            # 获取到输入框的数据
            goods_text = self.impot_goods_text.get(1.0, tkinter.END)
            print(goods_text)
            if goods_text.strip():
                goods_id = [int(i) for i in goods_text.split() if i]
            else:
                tkinter.messagebox.showinfo('！！', '请输入商品ID 后进行操作！')
                return


            print('要创建任务了')
            # 创建多线程进行更新
            self.thread_task[self.select_user_key] = threading.Thread(target=self.update_goods_id_task,
                                                                      args=(goods_id, user_obj, operator_dict, ))
            self.thread_task[self.select_user_key].start()
            print(goods_id)

        except Exception as e:
            tkinter.messagebox.showerror('输入有误', '%s' % e)

    # 线程内的任务， 根据商品ID更新商品
    def update_goods_id_task(self, goodlist, user_obj, operator_dict):
        # 清空table
        for _ in map(self.goods_list_table.delete, self.goods_list_table.get_children("")):
            pass
        try:
            for good in goodlist:
                time.sleep(10)
                # 获取草稿ID
                info, goods_commit_id = user_obj.get_goods_commit_id(good)
                if not info:
                    print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good, goods_commit_id))
                    self.goods_list_table.insert("", "end",
                                                 values=(good, '根据商品ID更新信息', goods_commit_id))
                    self.goods_list_table.update()
                    continue
                print('goods_commit_id', goods_commit_id)
                edit_json = user_obj.get_goods_edit_info(goods_commit_id)
                print('edit_json', edit_json)
                # 拼接完毕需要编辑的商品信息
                goods_json = user_obj.margen_post_date(edit_json, operator_dict)
                print('goods_json', goods_json)
                # 提交到草稿
                result, erromsg = user_obj.update_edit_goods(goods_json)
                print(result, erromsg)

                if not result:
                    print('[EERO]%s-->更新到草稿失败错误信息:[%s]' % (good, erromsg))
                    self.goods_list_table.insert("", "end",
                                                 values=(good, goods_json['goods_name'], erromsg))
                    self.goods_list_table.update()
                    continue
                # 提交到数据库
                result, erromsg = user_obj.commit_edit_goods(goods_commit_id, get_crawlerinfo())
                if not result:
                    print('[EERO]%s-->更新到数据库失败错误信息:[%s]' % (goods_json['goods_name'], erromsg))
                    self.goods_list_table.insert("", "end",
                                                 values=(good, goods_json['goods_name'], erromsg))
                    self.goods_list_table.update()
                    continue
                print('[SUCCESS]%s-->价格更新成功' % goods_json['goods_name'])
                self.goods_list_table.insert("", "end", values=(good, goods_json['goods_name'], erromsg))
                self.goods_list_table.update()
            tkinter.messagebox.showinfo('更新完毕', '更新完毕！')
        except Exception as e:
            print(e)
            tkinter.messagebox.showerror('错误', '当前商品更新失败！%s' % e)


    # 停止当前更新多页的任务
    def stop_update_task(self):
        if self.thread_task.get(self.select_user_key, None):
            if self.thread_task[self.select_user_key].isAlive():
                self.stop_thread(self.thread_task[self.select_user_key])
                self.thread_task.pop(self.select_user_key)
                tkinter.messagebox.showinfo('信息', '当前用户的任务成功')

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


if __name__ == '__main__':
    a = PddGUI()
    # cookies = None
    # with open('userinfo.pdd', 'r') as f:
    #     a = json.loads(f.read())
    #     print(a)
    #     cookies = a['cookies']
    # a = PddUpdate(cookies)
    # print(a.get_goods_commit_id('152145413546')) # (False, '商品不存在')
