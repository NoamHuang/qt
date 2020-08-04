#!/usr/bin/python3
# -*- coding:utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *

from PyQt5.QtCore import QFileInfo,QUrl
from PyQt5.QtWidgets import (QApplication)

import sys
import ctypes
import subprocess
import configparser
import os

startupFullScreen = False;
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()
        self.manager = Manager(QWidget)
        self.profile.setRequestInterceptor(self.manager)
        conf = self.getDir()
        startupFullScreen = conf.getboolean("client", "startup.full-screen")
        print(startupFullScreen)
        if startupFullScreen:
            self.showFullScreen()    #   如果要QT全屏
        else:
            self.showMaximized()
    # @pyqtSlot()     #   鼠标点击事件
    # def on_click(self):
    #     self.page.load(QUrl(excelUrl));

    def getDir(self):
        root_dir = os.path.abspath('.')  # 获取当前文件所在目录的上一级目录，即项目所在目录D:\PycharmProjects\configparser\qtConfigparser
        conf = configparser.ConfigParser()
        print(conf)
        print(root_dir)
        conf.read(root_dir + "\config.ini",encoding="utf-8-sig")  # 拼接得到config.ini文件的路径，直接使用
        # print("读取正常")
        return  conf

    def getAddress(self):
        conf = self.getDir()
        ip = conf.get("platform", "ip")  # 获取ip
        port = conf.get("platform", "port")  # 获取port
        protocol = conf.get("platform", "protocol")
        num = conf.get("platform", "num")
        address = protocol + '://' + ip + ':' + port+'?num='+num
        print(address)
        return address

        # 检测键盘回车按键，函数名字不要改，这是重写键盘事件
    def keyPressEvent(self, event):
        # print("按下：" + str(event.key()))    # 这里event.key（）显示的是按键的编码

        # 举例，这里Qt.Key_A注意虽然字母大写，但按键事件对大小写不敏感
        if (event.key() == Qt.Key_Escape):
            # print('测试：ESC')
            self.showNormal()
        if (event.key() == Qt.Key_F11):
            # print('测试：F11')
            self.showFullScreen()
        if (event.key() == Qt.Key_F12):
            # print('测试：F12')
            self.showMaximized()
        #
        if (event.key() == Qt.Key_Equal):
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                # print("CTRL =")
                self.browser.setZoomFactor(self.browser.zoomFactor() + 0.1)
        if (event.key() == Qt.Key_Minus):
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                # print("CTRL -")
                self.browser.setZoomFactor(self.browser.zoomFactor()-0.1)

    def initUI(self):
        conf = self.getDir()
        name = conf.get("client", "name")
        logo = conf.get("client", "logo")
        # width = conf.getint("client", "width")
        # height = conf.getint("client", "height")

        self.setWindowTitle(name)  # 设置窗口标题
        self.setWindowIcon(QIcon(logo))  # 设置任务栏图标
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("stu")  # 强制使用单独的AppUserModelID ，现在这个窗口拥有了一个新资源支配权限
        # self.resize(width, height)
        self.page = QWebEnginePage()
        self.profile = self.page.profile()
        self.browser = MyEngineView()
        self.browser.setPage(self.page)
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)  # 页面上禁用右键菜单#首页更新后，打开此页右键Reload解决缓存问题
        self.page.settings().setAttribute(QWebEngineSettings.PluginsEnabled, 1)
        address=self.getAddress()
        self.browser.setUrl(QUrl(address))  # 打开登陆页的URL
        self.setCentralWidget(self.browser)  # 将网页放入窗口中

class MyEngineView(QWebEngineView):     #浏览器类。

    def __init__(self, parent=None, ):
        super(MyEngineView, self).__init__(parent)
        self.parent = parent
        # 有下载信号发起
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
        # self.page().profile().setCachePath("C:/Users/Default/AppData/Local/stu")
        self.page().profile().clearHttpCache()

    def createWindow(self, type):
        '''
        实现点击跳转链接。
        '''
        return self

    def on_downloadRequested(self, download: "QWebEngineDownloadItem"):
        # download是QWebEngineDownloadItem对象；
        download.downloadProgress.connect(self._downloadProgress)
        download.finished.connect(self._finished)

        # 下载文件的保存路径及文件名
        old_path = download.path()
        suffix = QFileInfo(old_path).suffix()
        # 下载文件类型
        filttype = download.mimeType()
        # 后缀切割
        unkonw_suffix = filttype.split(r'/')[-1]
        path, _ = QFileDialog.getSaveFileName(self, "保存文件", old_path, "*." + unkonw_suffix + ";;" + "*." + suffix)

        print(old_path, suffix)

        if path != "":
            download.setPath(path)
            download.accept()

    def _downloadProgress(self, bytesReceived: "qint64", bytesTotal: "qint64"):
        # bytesReceived 当前下载值 ； bytesTotal 文件总大小值
        self.bytesReceived = bytesReceived
        self.bytesTotal = bytesTotal
        print(bytesReceived, bytesTotal)

    def _finished(self):
        print("下载完成")

class Manager(QWebEngineUrlRequestInterceptor): #监听事件
    def __init__(self,table):
        QWebEngineUrlRequestInterceptor.__init__(self)
        self.table = table

    def interceptRequest(self, reply):
        url = reply.requestUrl().toString()

if __name__ == "__main__":
    app = QApplication(sys.argv)  # 创建应用
    window = MainWindow()  # 创建主窗口
    sys.exit(app.exec_())  # 运行应用，并监听事件
    # 打包命令：pyinstaller stu.py -w --icon=logo.ico