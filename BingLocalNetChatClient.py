# 冰氏局域网去中心化聊天系统 - 客户端
# 作者注: 只是原则上的去中心化, 实际上一旦掌握密钥就可以通过客户端的一些后门进行控制

# 库导入
from PySide2.QtWidgets import QApplication, QMessageBox, QInputDialog, QLineEdit, QMainWindow, QWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import  QIcon, QFontDatabase, QPixmap
from threading import Thread
from win10toast_click import ToastNotifier
from PIL import ImageGrab
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import socket,time,sys,configparser,os,uuid,wget,requests,yaml

localHost = ''

# INI 配置文件
class Config:
    def __init__(self, file):
        self.file = file
        if not os.path.exists(self.file):
            cf = configparser.ConfigParser()
            # 不存在配置文件时创建配置文件
            cf.add_section("common")
            cf.set("common", "chat_host", '255.255.255.255')
            cf.set("common", "chat_port", '30930')
            cf.set('common', "file_port", "62059")
            cf.set('common', 'broadcast_port', '31129')
            cf.write(open(self.file, 'w', encoding='utf-8'))

        self.config = configparser.ConfigParser()
        self.config.read(self.file)

    def writeConfig(self, section, option, value):
        self.config.set(section, option, value)
        self.config.write(open(self.file, "w", encoding="utf-8"))
        self.config.read(self.file)

# YAML 配置文件
class YamlConfig:
    def __init__(self, file):
        self.file = file
        if not os.path.exists(self.file):
            data = {'username': ''}
            with open(self.file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f)

        with open(self.file, 'r', encoding="utf-8") as f:
            self.config = f.read()

    def getConfig(self):
        return yaml.load(self.config, Loader=yaml.FullLoader)

    def writeConfig(self, key, value):
        data = self.getConfig()
        data[key] = value

        with open(self.file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)

        with open(self.file, 'r', encoding="utf-8") as f:
            self.config = f.read()

# 下载文件
def downloadFile(url ,path):
    wget.download(url, path)
    
    r = requests.get(url, stream=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):  # 1024 bytes
            if chunk:
                f.write(chunk)

# 关于我们
class About(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load('style/About.ui')
        self.ui.setWindowTitle("关于 冰氏局域网去中心化聊天系统")

        self.ui.label.setPixmap(QPixmap('style/25385f0f6af17a35.jpg'))

        self.ui.textBrowser.anchorClicked.connect(self.clickURL)

    # 点击链接
    def clickURL(self, url):
        os.startfile(url.toString())

# 主窗口
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = QUiLoader().load('style/MainWindow.ui')
        # Alpha
        self.ui.setWindowTitle("冰氏局域网去中心化聊天系统 - 客户端 - v1.0")

        self.ui.actionSetUserName.triggered.connect(self.setUserName)
        self.ui.actionChannelConnect.triggered.connect(self.changeChannel)
        self.ui.actionExit.triggered.connect(self.exitClient)
        self.ui.actionAbout.triggered.connect(self.openAbout)
        self.ui.actionClearChat.triggered.connect(self.clearChat)

        self.ui.textBrowser.anchorClicked.connect(self.clickURL)

        # 发送按钮
        self.ui.sendButton.clicked.connect(self.sendMsg)
        self.ui.screenshotButton.clicked.connect(self.sendScreenshot)

        # 如果没有设置用户名, 询问用户名
        if yamlConfig.getConfig()['username'] == '':
            while True:
                title, okPressed = QInputDialog.getText(self, "填写昵称", "设置你的昵称为：", QLineEdit.Normal, "")

                if okPressed and title != "":
                    #config.writeConfig("common", "username", title)
                    yamlConfig.writeConfig('username', title)
                    break

    # 发送信息
    def sendMsg(self):
        try:
            # 如果为空则不发送
            if self.ui.sendText.toPlainText() == "": return

            data = {'username': yamlConfig.getConfig()['username'], 'type':'msg', 'text':self.ui.sendText.toPlainText()}
            sender.sendMsg(data)
            self.ui.sendText.clear()

            # 提交一份自己的
            main.ui.textBrowser.append('')
            main.ui.textBrowser.append('<b><font color="#4CAF50">{}</font></b>'.format('[{}] 你:'.format(time.strftime("%H:%M:%S", time.localtime()))))
            for line in data['text'].split('\n'):
                main.ui.textBrowser.append('<font color="#4CAF50">{}</font>'.format(line))
            main.ui.textBrowser.ensureCursorVisible()
        except:
            QMessageBox.critical(self.ui, '错误', '发送信息错误')

    # 发送屏幕截图
    def sendScreenshot(self):
        im = ImageGrab.grab()
        fileID = uuid.uuid1()
        fileName = str(fileID)
        im.save('cache/{}.jpg'.format(fileID), 'jpeg')

        try:
            data = {'username': yamlConfig.getConfig()['username'], 'type':'img', 'port':config.config['common']['file_port'], 'file':'{}.jpg'.format(fileName)}
            sender.sendMsg(data)

            main.ui.textBrowser.append('')
            main.ui.textBrowser.append('<b><font color="#4CAF50">{}</font></b>'.format('[{}] 你:'.format(time.strftime("%H:%M:%S", time.localtime()))))
            main.ui.textBrowser.append('<a href="file:///{path}\cache\{file}"><img src="cache/{file}" width=500></a>'.format(file=str(fileName) + '.jpg', path=os.getcwd()))
            main.ui.textBrowser.ensureCursorVisible()
        except:
            QMessageBox.critical(self.ui, '错误', '发送屏幕截图错误')

    # 设置昵称
    def setUserName(self):
        title, okPressed = QInputDialog.getText(self, "填写昵称", "设置你的昵称为：", QLineEdit.Normal, yamlConfig.getConfig()['username'])

        if okPressed and title == "":
            QMessageBox.critical(self.ui, '警告', '昵称不可为空')
        elif okPressed:
            yamlConfig.writeConfig('username', title)
            QMessageBox.information(self.ui, '设置成功', '你已成功将昵称修改为 {}'.format(title))

    # 切换频道
    def changeChannel(self):
        global nowChatChannel, listener, sender, th_listener

        title, okPressed = QInputDialog.getInt(self, "更换频道", "输入相应频道的端口：", QLineEdit.Normal, 0)

        if okPressed and 0 <= title <= 65535:
            nowChatChannel = title

            # 停止服务并重新启动
            listener = th_listener = None
            listener = Listener(nowChatChannel)
            th_listener = Thread(target=listener.run)
            th_listener.start()

            sender.changePort(nowChatChannel)

            # 输出提示
            main.ui.textBrowser.append('')
            main.ui.textBrowser.append('<b><font color="#F44336">{}</font></b>'.format('[提示] 你已成功将端口修改为 {}...'.format(nowChatChannel)))
            main.ui.textBrowser.ensureCursorVisible()

        elif okPressed:
            QMessageBox.critical(self.ui, '警告', '频道端口超出范围 (0 - 65535)')

    # 退出程序
    def exitClient(self):
        choice = QMessageBox.question(self.ui, '确认退出', '退出后不保留历史记录')
        if choice == QMessageBox.Yes: os._exit(0)

    # 清除聊天
    def clearChat(self):
        self.ui.textBrowser.clear()
        statusBar.addStatus('已成功清除聊天记录')

    # 打开关于
    def openAbout(self):
        about.ui.show()

    # 点击链接
    def clickURL(self, url):
        os.startfile(url.toString())

# 发送者 Sender
class Sender:
    # 初始化时需要 username
    def __init__(self, network, port):
        self.network = network
        self.port = port

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # 加入信息
        data = {'username': yamlConfig.getConfig()['username'], 'type': "join"}
        self.sendMsg(data)
    # 发送数据
    def sendMsg(self, data):
        self.s.sendto(str(data).encode("utf-8"), (self.network, self.port))
    def close(self):
        self.s.close()
    def changePort(self, port):
        # 离开信息
        data = {'username': yamlConfig.getConfig()['username'], 'type': "quit"}
        self.sendMsg(data)
        # 更换端口
        self.port = port
        # 加入信息
        data = {'username': yamlConfig.getConfig()['username'], 'type': "join"}
        self.sendMsg(data)

# 接收者 Listener
class Listener:
    def __init__(self, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        time.sleep(0.1)
        self.s.bind(('', port))

    # 获取到数据时的操作
    def run(self):
        while True:
            rawData, address = self.s.recvfrom(65535)
            data = eval(rawData)
            print('[DEBUG] Server received from {}:{}'.format(address, rawData.decode('utf-8')))

            # 如果是本地发送的, 则忽略
            if address[0] == localHost:
                #time.sleep(0.2)
                continue

            # 显示
            if data['type'] == 'msg':
                main.ui.textBrowser.append('')
                main.ui.textBrowser.append('<b>[{}] {}({}):</b>'.format(time.strftime("%H:%M:%S", time.localtime()), data['username'], address[0]))
                main.ui.textBrowser.append(data['text'])
                main.ui.textBrowser.ensureCursorVisible()

                # Win10 推送
                self.sendWindowsMessage("你收到了来自 {}({}) 的信息".format(data['username'], address[0]), data['text'])
            elif data['type'] == 'img':
                # 下载
                #wget.download('http://{}:{}/{}'.format(address[0], data['port'], data['file']), 'cache/{}'.format(data['file']))
                downloadFile('http://{}:{}/{}'.format(address[0], data['port'], data['file']), 'cache/{}'.format(data['file']))

                # 输出文本
                main.ui.textBrowser.append('')
                main.ui.textBrowser.append('<b>[{}] {}({}):</b>'.format(time.strftime("%H:%M:%S", time.localtime()), data['username'], address[0]))
                main.ui.textBrowser.append('<a href="file:///{path}\cache\{file}"><img src="cache/{file}" width=500></a>'.format(file=data['file'], path=os.getcwd()))
                main.ui.textBrowser.ensureCursorVisible()

                # Win10 推送
                self.sendWindowsMessage("你收到了来自 {}({}) 的信息".format(data['username'], address[0]), '[屏幕截图]')
            elif data['type'] == 'join':
                main.ui.textBrowser.append('')
                main.ui.textBrowser.append('<b><font color="#3F51B5">{}</font></b>'.format('[系统] 用户 {}({}) 进入了此频道'.format(data['username'], address[0])))
                main.ui.textBrowser.ensureCursorVisible()

            elif data['type'] == 'exit':
                main.ui.textBrowser.append('')
                main.ui.textBrowser.append('<b><font color="#3F51B5">{}</font></b>'.format('[系统] 用户 {}({}) 离开了此频道'.format(data['username'], address[0])))
                main.ui.textBrowser.ensureCursorVisible()

    # Windows 10 消息
    def sendWindowsMessage(self, title, message):
        try:
            toaster.show_toast(title, message, icon_path="logo.ico", threaded = True, duration = None)
        except:
            print("[警告] 发送 Windows 消息出错")

# 文件传输服务
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='cache', **kwargs)

class fileHttp:
    def __init__(self):
        self.server_obj = None
        if not os.path.exists('cache'):
            os.makedirs('cache')

    def run(self):
        self.server_obj = ThreadingHTTPServer(('', config.config['common'].getint('file_port')), Handler)
        self.server_obj.serve_forever()

# 底部提示框
class StatusBar:
    def __init__(self):
        self.statusbar = main.ui.statusbar
        self.status = []

        self.th_statusbar = Thread(target=self.run)
        self.th_statusbar.start()

    def run(self):
        while True:
            if len(self.status) > 0:
                self.statusbar.showMessage(self.status.pop(0))
                time.sleep(7)
            else:
                self.statusbar.showMessage("你当前使用昵称 {} 位于 {} 频道".format(yamlConfig.getConfig()['username'], nowChatChannel))
            time.sleep(0.5)

    def addStatus(self, status):
        self.status.append(status)

# TODO 管理员：软件更新、禁言、强制关闭软件

# Windows 通知
toaster = ToastNotifier()

# 主函数
if __name__ == '__main__':
    # 获取本机地址
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    localHost = s.getsockname()[0]
    s.close()

    # 读取配置
    config = Config('config.ini')
    yamlConfig = YamlConfig('config.yml')

    # 准备文件和图片的传输
    file_http = fileHttp()
    th_fileHttp = Thread(target=file_http.run)
    th_fileHttp.start()

    # 基础加载
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont("font/HarmonyOS_Sans_SC_Black.ttf")
    QFontDatabase.addApplicationFont("font/HarmonyOS_Sans_SC_Bold.ttf")
    QFontDatabase.addApplicationFont("font/HarmonyOS_Sans_SC_Light.ttf")
    QFontDatabase.addApplicationFont("font/HarmonyOS_Sans_SC_Medium.ttf")
    QFontDatabase.addApplicationFont("font/HarmonyOS_Sans_SC_Regular.ttf")
    QFontDatabase.addApplicationFont("font/HarmonyOS_Sans_SC_Thin.ttf")
    app.setWindowIcon(QIcon('logo.png'))
    main = MainWindow()
    main.ui.show()
    about = About()

    # 将聊天频道传给变量, 以便调用
    nowChatChannel = config.config['common'].getint('chat_port')

    # 启动状态管理器
    statusBar = StatusBar()

    # 提示连接到默认频道
    main.ui.textBrowser.append('')
    main.ui.textBrowser.append('<b><font color="#F44336">{}</font></b>'.format('[提示] 你已成功连接到默认频道...'))
    main.ui.textBrowser.ensureCursorVisible()

    # 监听聊天频道
    listener = Listener(nowChatChannel)
    th_listener = Thread(target=listener.run)
    th_listener.start()

    # 发送端
    sender = Sender(config.config['common']['chat_host'], nowChatChannel)

    # 退出准备
    app.exec_()
    os._exit(0)