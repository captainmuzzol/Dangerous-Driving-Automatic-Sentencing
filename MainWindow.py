# coding=utf-8
# 本程序（包括其他文件，如"ExtraDef.py","WXJS_newPdfget"等）用于对简单案件进行基础解析和文书生成，目的是为了提高检察官办案效率。代码公开未加密，请勿商用或用作其他营利用途！
# 最后一次更新：2023.6.9/2024.6.19
import os
import re
import sys
import zipfile

import fitz
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import WXJS_newPdfget

global file_load
file_load = os.getcwd()
global mylogs
mylogs = ''


class NewQLineEdit(QtWidgets.QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)  # 删除没有影响，目前不确定（因为True和False测试结果一样）
        self.setDragEnabled(True)  # 删除没有影响，（因为True和False测试结果一样）

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():  # 当文件拖入此区域时为True
            event.accept()  # 接受拖入文件
        else:
            event.ignore()  # 忽略拖入文件

    def dropEvent(self, event):  # 本方法为父类方法，本方法中的event为鼠标放事件对象
        urls = [u for u in event.mimeData().urls()]  # 范围文件路径的Qt内部类型对象列表，由于支持多个文件同时拖入所以使用列表存放
        for url in urls:
            self.setText(url.path()[1:])  # 将Qt内部类型转换为字符串类型


class Ui_MainWindow(QWidget):
    global mylogs
    mylogs = ""
    def __init__(self):
        super().__init__()
        self._startPos = None
        self._endPos = None
        self._tracking = False
        self.resize(733, 500)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setAcceptDrops(True)

        # 设置背景图
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 0, 681, 451))
        self.label.setText("")
        # 还需要获取绝对路径？
        file_load = os.getcwd()
        self.label.setPixmap(QtGui.QPixmap(file_load + r'/image/背景图.png'))
        self.label.setScaledContents(True)
        self.label.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # label = QLabel("我是一个窗体，但我没有边框！！！", self)
        # label.move(6, 6)

        # 设置输入框
        self.lineEdit = NewQLineEdit(self)  # 此处更改
        self.lineEdit.setGeometry(QtCore.QRect(220, 51, 390, 55))
        self.lineEdit.setAcceptDrops(True)
        self.lineEdit.setStyleSheet("font: 12pt \"Arial\";")
        self.lineEdit.setText("(等待中)>>")
        self.lineEdit.setObjectName("lineEdit")

        # 设置标签
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(55, 60, 211, 41))
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(50, 160, 651, 180))
        self.label_2.setStyleSheet("color: black")
        self.label_3.setStyleSheet("color: black")
        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setGeometry(QtCore.QRect(495, 290, 651, 180))
        self.label_4.setStyleSheet("font: 11pt; color: gray;")
        #self.label_4.setStyleSheet("")

        # 设置按钮
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(420, 113, 161, 41))
        font = QtGui.QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.setStyleSheet("QPushButton {\n"
                                      "    background-color: #ffffff;\n"
                                      "    border: 1px solid #dcdfe6;\n"
                                      "    padding: 10px;\n"
                                      "    border-radius: 5px;\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover {\n"
                                      "    background-color: #ecf5ff;\n"
                                      "    color: #409eff;\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed, QPushButton:checked {\n"
                                      "    border: 1px solid #3a8ee6;\n"
                                      "    color: #409eff;\n"
                                      "}\n"
                                      "\n"
                                      "#button3 {\n"
                                      "    border-radius: 20px;\n"
                                      "}")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("开始计算")
        self.pushButton.clicked.connect(self.extractZipFiles)
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(330, 350, 156, 40))
        font = QtGui.QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(14)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_2.setStyleSheet("QPushButton {\n"
                                        "    background-color: #ffffff;\n"
                                        "    border: 1px solid #dcdfe6;\n"
                                        "    padding: 10px;\n"
                                        "    border-radius: 5px;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: #ecf5ff;\n"
                                        "    color: #409eff;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed, QPushButton:checked {\n"
                                        "    border: 1px solid #3a8ee6;\n"
                                        "    color: #409eff;\n"
                                        "}\n"
                                        "\n"
                                        "#button3 {\n"
                                        "    border-radius: 20px;\n"
                                        "}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.on_pushButton_2_clicked)
        self.pushButton_2.setText("生成文书")
        # self.pushButton_2.clicked.connect(self.close)
        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(215, 350, 110, 41))
        self.pushButton_3.setFont(font)
        self.pushButton_3.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_3.setStyleSheet("QPushButton {\n"
                                        "    background-color: #ffffff;\n"
                                        "    border: 1px solid #dcdfe6;\n"
                                        "    padding: 10px;\n"
                                        "    border-radius: 5px;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: #ecf5ff;\n"
                                        "    color: #409eff;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed, QPushButton:checked {\n"
                                        "    border: 1px solid #3a8ee6;\n"
                                        "    color: #409eff;\n"
                                        "}\n"
                                        "\n"
                                        "#button3 {\n"
                                        "    border-radius: 20px;\n"
                                        "}")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setText("结果调整")
        self.pushButton_3.clicked.connect(self.change_LX)  # 打开调整窗口

        # 手动量刑窗口按钮
        self.pushButton_4 = QtWidgets.QPushButton(self)
        self.pushButton_4.setGeometry(QtCore.QRect(60, 350, 150, 41))
        self.pushButton_4.setFont(font)
        self.pushButton_4.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_4.setStyleSheet("QPushButton {\n"
                                        "    background-color: #ffffff;\n"
                                        "    border: 1px solid #dcdfe6;\n"
                                        "    padding: 10px;\n"
                                        "    border-radius: 5px;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: #ecf5ff;\n"
                                        "    color: #409eff;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed, QPushButton:checked {\n"
                                        "    border: 1px solid #3a8ee6;\n"
                                        "    color: #409eff;\n"
                                        "}\n"
                                        "\n"
                                        "#button3 {\n"
                                        "    border-radius: 20px;\n"
                                        "}")
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setText("手动危驾量刑")
        self.pushButton_4.clicked.connect(self.hand_LX)  # 打开调整窗口

        # 设置进度条
        self.progressBar = QtWidgets.QProgressBar(self)
        # self.progressBar.setGeometry(QtCore.QRect(40, 400, 632, 10))
        self.progressBar.setGeometry(QtCore.QRect(40, 405, 632, 10))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setVisible(0)
        self.progressBar.setObjectName("progressBar")

        # 设置下拉按钮
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(250, 115, 151, 38))
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("等待传入识别")
        self.comboBox.addItem("识别失败")
        self.comboBox.addItem("危险驾驶")
        self.comboBox.addItem("交通肇事")
        self.comboBox.addItem("盗窃")
        self.comboBox.setCurrentIndex(0)
        self.comboBox.setEnabled(False)  # 下拉框不可选中

        self.comboBox_2 = QtWidgets.QComboBox(self)
        self.comboBox_2.setGeometry(QtCore.QRect(110, 115, 121, 38))
        self.comboBox_2.setFont(font)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("选择检察官")
        self.comboBox_2.addItem("通用")
        self.comboBox_2.addItem("陈一林")
        self.comboBox_2.addItem("丁林")
        # self.comboBox_2.addItem("")
        self.comboBox_2.setCurrentIndex(0)
        # 设置为已经保存过的检察官
        try:
            with open(file_load + r'/模板/inquisitor.txt') as file:
                inquisitor = file.read()
            for i in range(0, 4):
                self.comboBox_2.setCurrentIndex(i)
                if self.comboBox_2.currentText() == inquisitor:
                    break
                else:
                    i += 1
        except:
            pass

        # 设置字体和内容
        font = QtGui.QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setText("拖入案卷压缩包：")
        self.label_2.setObjectName("label_2")
        font = QtGui.QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setText("                         拖入压缩包后，请先点击“开始计算”，再点击“生成文书”\n                                                        (建议↙手动计算)")
        self.label_3.setObjectName("label_3")
        font = QtGui.QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setText("简案文书生成器2.6.0\n  测试版，请勿外传")
        self.label_4.setObjectName("label_4")

        # 添加红色圆圈(关闭按钮)
        self.close_button = QtWidgets.QPushButton(self)
        self.close_button.setGeometry(QtCore.QRect(625, 27, 30, 30))
        self.close_button.setStyleSheet("background-color:red;border-radius:15px;")
        self.close_button.clicked.connect(self.close)

        # 窗体置顶(窗体置顶，仅仅为了方便测试)，去边框
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 窗体透明，控件不透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置窗口透明度
        self.setWindowOpacity(0.91)

    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        if self._tracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._startPos = QPoint(e.x(), e.y())
            self._tracking = True

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    def extractZipFiles(self):
        print('MainWindow调试信息：进入exTractFiles函数')
        LX_final = ''
        global dest_folder

        self.zip_file_path = self.lineEdit.text()  # 将lineEdit中的值设置为默认 Windows

        # 检察官判断
        file_load = os.getcwd()
        if self.comboBox_2.currentText() == "陈一林":
            print("测试2")
            with open(file_load + "/模板/inquisitor.txt", "w", encoding='gbk') as inquisitor_file:
                print("测试")
                inquisitor_file.write("陈一林")
        elif self.comboBox_2.currentText() == "丁林":
            with open(file_load + "/模板/inquisitor.txt", "w", encoding='gbk') as file:
                file.write("丁林")
        elif self.comboBox_2.currentText() == "王佳":
            with open(file_load + "/模板/inquisitor.txt", "w", encoding='gbk') as file:
                file.write("王佳")
        else:
            with open(file_load + "/模板/inquisitor.txt", "w", encoding='gbk') as file:
                file.write("通用")
            print("未通过")
        # if not hasattr(self, 'zip_file_path'):
        # print('调试信息：进入if not hasattr(selfzip_file_path')
        # zip_file_path = '/' + self.lineEdit.text()      # Mac
        zip_file_path = self.lineEdit.text()  # Windows
        print(zip_file_path)
        if not os.path.exists(zip_file_path):
            self.lineEdit.setText("文件路径不存在！")
            return
        self.zip_file_path = zip_file_path
        if "危险驾驶" in zip_file_path:
            self.comboBox.setCurrentIndex(2)  # 下拉框设置为危险驾驶
        elif "盗窃" in zip_file_path:
            self.comboBox.setCurrentIndex(4)  # 下拉框设置为盗窃

        zip_file = zipfile.ZipFile(self.zip_file_path)
        dest_folder = os.path.join(os.path.dirname(self.zip_file_path),
                                   os.path.splitext(os.path.basename(self.zip_file_path))[0])

        pdf_files = []
        try:
            for name in zip_file.namelist():
                print("MainWindow调试信息：进入for name in zip_file.namelist()")
                if name.endswith(".pdf"):
                    zip_file.extract(name, dest_folder)
                    pdf_files.append(os.path.join(dest_folder, name))
        except:
            pass
        self.lineEdit.setText(dest_folder)
        self.lineEdit.setText("计算完成！现在可以点击“生成文书”按钮。")
        self.progressBar.setValue(0)

        # 打开PDF文件并获取书签信息
        pdf_path = dest_folder + '/诉讼文书卷.pdf'
        with fitz.open(pdf_path) as pdf_file:
            toc = pdf_file.get_toc()
        # 查找书签中标题包含“起诉意见书”的页码范围
        target = '起诉意见书'

        # 获取起诉意见书的页码
        num = 0
        for i in range(len(toc)):
            if target in toc[i][1]:
                if i + 1 < len(toc):
                    qsyjs_page_get = (toc[i + 1][1])
                    qsyjs_page = re.search('\d+', qsyjs_page_get)
                    if qsyjs_page:
                        num = int(qsyjs_page.group(0))
                        # print(num)
                    else:
                        print('未找到起诉意见书页码')
                else:
                    print('未找到起诉意见书')

        # 提取起诉意见书的文本
        # 由于fitz的页面索引从0开始，因此从num-1开始
        doc = fitz.open(pdf_path)
        # 提取页码
        page1 = doc.load_page(num - 1)
        page2 = doc.load_page(num)

        # 提取文本内容
        text14 = page1.get_text()
        text15 = page2.get_text()

        # 拼接文本内容
        combined_text = text14 + "\n\n" + text15
        # 将文本内容写入txt文件
        with open("output.txt", "w", encoding="gbk") as file:
            print("MainWindow调试信息：成功打开output")
            file.write(combined_text)
        # 关闭文档
        doc.close()
        # 删除pdf文件夹
        # shutil.rmtree(dest_folder)
        print("MainWindow调试信息：成功走到这一步")
        LX_result = WXJS_newPdfget.LX("output.txt")
        # print('调试信息：LX_result', LX_result)
        self.label_3.setText(LX_result)
        if LX_result.find("不起诉处理") != -1:
            LX_final = LX_result[LX_result.find("建议量刑："):(LX_result.find("处理") + 2)]
            LX_final = LX_final + "\n 因识别内容有限，本量刑仅供参考，请在左下角点击手动量刑更准确！"
        else:
            LX_final = LX_result[LX_result.find("建议量刑："):(LX_result.find("元") + 1)]
            LX_final = LX_final + "\n 因识别内容有限，本量刑仅供参考，请在左下角点击手动量刑更准确！"

        # 把量刑结果写入txt
        txt_load = file_load + "/模板/LX_change.txt"
        with open(txt_load, "w", encoding="gbk") as txt_file:
            txt_file.write(LX_final)
        print('MainWindow调试信息：LX_final写入LX_change成功')

    def on_pushButton_2_clicked(self):
        # 修改量刑
        print("MainWindow调试信息：label_3:", self.label_3.text())
        text_2 = self.label_3.text()
        print("MainWindow调试信息：text2:", text_2)
        if text_2.startswith("建议量刑"):
        # if "建议量刑" in text_2:
            try:
                with open(file_load + "/模板/LX_change.txt", "w", encoding='gbk') as LX_file:
                    LX_file.write(text_2)
            except:
                pass
        else:
            pass
        self.progressBar.setVisible(1)
        self.progressBar.setValue(15)  # 进度条10%
        try:
            import WXJS_Pdfget
            self.progressBar.setValue(60)  # 进度条20%
            WXJS_Pdfget.SC('output.txt')
            self.progressBar.setValue(65)  # 进度条50%
            print('MainWindow调试信息：import WXJS_Pdfget成功')
            import ScbgScan
            self.progressBar.setValue(70)  # 进度条60%
            # pdf_file = dest_folder + '/诉讼证据卷.pdf'
            # page = ScbgScan.get_bookmarks(pdf_file)
            # print(page[0])
            self.progressBar.setValue(75)  # 进度条75%
            self.progressBar.setValue(100)  # 进度条100%
            msgBox = QMessageBox()
            msgBox.setWindowTitle("完成")
            msgBox.setText("文件已经生成至桌面！")
            msgBox.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
            msgBox.exec_()
            # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        except:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("提示")
            msgBox.setText("文件因不明原因生成失败！请检查是否忘记点击“开始计算”按钮，或忘记拖入压缩包，或压缩包中文件错误。")
            msgBox.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
            msgBox.exec_()

    def change_LX(self):
        # 打开调整窗口
        text = ''
        self.second_window = SecondWindow(text)
        self.second_window.exec_()
        jylx = ""
        try:
            jylx = ""
        except:
            jylx = "获取错误"
        jylx = "▶>>>建议量刑：" + self.second_window.text_edit + "个月" + self.second_window.text_edit2 + "天<<<◀"
        self.label_3.setText(jylx)

    def hand_LX(self):
        # 打开手动量刑窗口
        self.third_window = ThirdWindow()
        self.third_window.show()

# 调整量刑窗口
class SecondWindow(QDialog):
    def __init__(self, text):
        super().__init__()

        # self.text_edit = QTextEdit(text)
        # self.text_edit2 = QTextEdit(text)
        self.setWindowTitle('调整量刑')
        central_widget = QWidget()
        # self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        month_label = QLabel("请输入调整后的月数：")
        self.month_combo = QComboBox()
        for month in range(1,7):
            self.month_combo.addItem(str(month))
        layout.addWidget(month_label)
        layout.addWidget(self.month_combo)

        day_label = QLabel("请输入调整后的日数：")
        self.day_combo = QComboBox()
        self.day_combo.addItems(["0", "10", "15", "20"])
        layout.addWidget(day_label)
        layout.addWidget(self.day_combo)
        
        self.button = QPushButton('确认修改')
        self.button2 = QPushButton('改为不起诉')

        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        self.setLayout(layout)
        
        self.text_edit = self.month_combo.currentText()
        self.text_edit2 = self.day_combo.currentText()
        print(self.text_edit, "和",self.text_edit2)
        self.button.clicked.connect(self.update_label)

    def update_label(self):
        self.text_edit = self.month_combo.currentText()
        self.text_edit2 = self.day_combo.currentText()
        print(self.text_edit, "和", self.text_edit2)
        self.accept()

# 手动危险驾驶量刑
class ThirdWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("危险驾驶量刑计算器")
        self.alcohol_input = QLineEdit()
        self.alcohol_input.setPlaceholderText("请输入酒精含量：mg/100ml")
        # self.alcohol_input.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.alcohol_input.setFont(font)
        
        

        self.checkBoxDict = {
            "extra_case1": QCheckBox("造成事故且负全责或主责（自撞、无财产损失或极轻微损失不用勾选）"),
            "extra_case2" : QCheckBox("造成事故后逃逸"),
            "extra_case3" : QCheckBox("造成他人轻伤"),
            "extra_case4" : QCheckBox("未取得机动车驾驶证驾驶汽车"),
            "extra_case5" : QCheckBox("吊销、扣留、超年审一年、记分满12等无有效驾驶证的情形"),
            "extra_case6" : QCheckBox("服用国家规定管制的精神药品或麻醉药品后行驶"),
            "extra_case7" : QCheckBox("驾驶机动车从事校车业务且载有师生"),
            "extra_case8" : QCheckBox("驾驶重型载货汽车"),
            "extra_case9" : QCheckBox("运输危险化学品、危险货物"),
            "extra_case10" : QCheckBox("严重超员、超载、超速行驶"),
            "extra_case11" : QCheckBox("明知车辆性能不符合要求（汽车报废）"),
            "extra_case12" : QCheckBox("在高速公路上行驶"),
            "extra_case13" : QCheckBox("在诉讼期间不到案或逃跑"),
            "extra_case14" : QCheckBox("明显逃避、阻碍公安机关依法检查的"),
            "extra_case24" : QCheckBox("采取暴力手段抗拒公安机关依法检查或实施妨害司法行为"),
            "extra_case15" : QCheckBox("威胁、报复、引诱、贿买证人、鉴定等人员或毁灭、伪造证据妨害司法"),
            "extra_case16" : QCheckBox("二年内曾因饮酒后驾驶机动车被查获或受过行政处罚"),
            "extra_case17" : QCheckBox("五年内曾因危险驾驶行为被判有罪或作相对不起诉处理过"),
            "extra_case25" : QCheckBox("五年内曾因饮酒后驾驶被查获或受过行政处罚(注：与上下几个可重复勾选)"),
            "extra_case18" : QCheckBox("2年外:有酒后驾车的行政处罚劣迹;或5年外:有酒驾前科（含不起诉）一次"),
            "extra_case19" : QCheckBox("2年外:有酒后驾车的行政处罚劣迹;或5年外:有酒驾前科（含不起诉）多次"),
            "extra_case20" : QCheckBox("其他非同类前科劣迹"),
            "extra_case21" : QCheckBox("赔偿，并取得谅解"),
            "extra_case22" : QCheckBox("坦白、认罪认罚"),
            "extra_case23" : QCheckBox("自首、认罪认罚")
        }

        # 颜色设置
        self.checkBoxDict["extra_case1"].setStyleSheet("color:rgb(255,152,100);font-size: 14px;"),self.checkBoxDict["extra_case2"].setStyleSheet("color:rgb(255,152,0);font-size: 14px;"),self.checkBoxDict["extra_case3"].setStyleSheet("color:rgb(255,152,0);font-size: 14px;"),
        self.checkBoxDict["extra_case4"].setStyleSheet("color:red; font-size: 14px;"),self.checkBoxDict["extra_case5"].setStyleSheet("color:red; font-size: 14px;"),
        self.checkBoxDict["extra_case6"].setStyleSheet("color:rgb(3,101,100);font-size: 14px;"),self.checkBoxDict["extra_case7"].setStyleSheet("color:rgb(3,101,100);font-size: 14px;"),self.checkBoxDict["extra_case8"].setStyleSheet("color:rgb(3,101,100);font-size: 14px;"),self.checkBoxDict["extra_case9"].setStyleSheet("color:rgb(3,101,100);font-size: 14px;"),self.checkBoxDict["extra_case10"].setStyleSheet("color:rgb(3,101,100);font-size: 14px;"),self.checkBoxDict["extra_case11"].setStyleSheet("color:rgb(3,101,100);font-size: 14px;"),self.checkBoxDict["extra_case12"].setStyleSheet("color:rgb(3,101,100);font-size: 14px;"),
        self.checkBoxDict["extra_case13"].setStyleSheet("color:brown; font-size: 14px;"),self.checkBoxDict["extra_case14"].setStyleSheet("color:brown;font-size: 14px;"),self.checkBoxDict["extra_case15"].setStyleSheet("color:brown;font-size: 14px;"),self.checkBoxDict["extra_case24"].setStyleSheet("color:brown;font-size: 14px;")
        self.checkBoxDict["extra_case16"].setStyleSheet("color:black; font-size: 14px;"),self.checkBoxDict["extra_case17"].setStyleSheet("color:black; font-size: 14px;"),self.checkBoxDict["extra_case18"].setStyleSheet("color:black; font-size: 14px;"),self.checkBoxDict["extra_case19"].setStyleSheet("color:black; font-size: 14px;"),self.checkBoxDict["extra_case20"].setStyleSheet("color:black; font-size: 14px;"),self.checkBoxDict["extra_case21"].setStyleSheet("color:black; font-size: 14px;"),
        self.checkBoxDict["extra_case21"].setStyleSheet("color:blue;font-size: 14px;"),self.checkBoxDict["extra_case22"].setStyleSheet("color:blue;font-size: 14px;"),self.checkBoxDict["extra_case23"].setStyleSheet("color:blue;font-size: 14px;")

        self.calc_button = QPushButton('开始计算')
        self.calc_button.clicked.connect(self.calculate_LX)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("请输入酒精含量"))
        layout.addWidget(self.alcohol_input)

        # 设置关联逻辑
        self.checkBoxDict["extra_case22"].stateChanged.connect(self.onCheckboxchanged)
        self.checkBoxDict["extra_case23"].stateChanged.connect(self.onCheckboxchanged)
        self.checkBoxDict["extra_case18"].stateChanged.connect(self.onCheckboxchanged2)
        self.checkBoxDict["extra_case19"].stateChanged.connect(self.onCheckboxchanged2)
        self.checkBoxDict["extra_case14"].stateChanged.connect(self.onCheckboxchanged3)
        self.checkBoxDict["extra_case24"].stateChanged.connect(self.onCheckboxchanged3)

        # 加粗：将复选框状态改变的信号连接到定义的槽函数
        for checkBox in self.checkBoxDict.values():
            checkBox.stateChanged.connect(self.toggleFontBold)
            layout.addWidget(checkBox)
 
        layout.addWidget(self.calc_button)

        self.setLayout(layout)
        # self.set(self.window)

    # 计算刑期
    def calculate_LX(self):
        jjhl = 0
        jishu = 0
        beichengshu = 1
        shixing = 0
        sx_reason = ""
        LX_bef = 0
        LX_aft = ""
        hx = 0
        fj = 0
        bqs = 0
        
        # 数值有效性检测
        try:    
            jjhl = int(self.alcohol_input.text())
        except:
            print("还未输入")

        jishu = jjhl/80
        
        # 实刑项目
        for num in [2,3,4,6,24,25]:     
            if self.checkBoxDict[f"extra_case{num}"].isChecked():
                shixing = 1
                sx_reason += (self.checkBoxDict[f"extra_case{num}"].text() + "、")
        if jjhl > 180:
            shixing = 1
            sx_reason += "酒精含量大于180mg/100ml"

        # 额外情节
        for num in [1,2,4,6,9,10,14,15,16,17,24]:     
            if self.checkBoxDict[f"extra_case{num}"].isChecked():
                jishu += 1
        for num in [7,8,12]:     
            if self.checkBoxDict[f"extra_case{num}"].isChecked():
                jishu += 2
        for num in [18,20]:     
            if self.checkBoxDict[f"extra_case{num}"].isChecked():
                beichengshu += 0.05  
        for num in [3,5,11,13,19]:     
            if self.checkBoxDict[f"extra_case{num}"].isChecked():
                beichengshu += 0.1      
        if self.checkBoxDict["extra_case21"].isChecked():   # 赔偿谅解
            beichengshu -= 0.15 
        if self.checkBoxDict["extra_case22"].isChecked():   # 赔偿谅解
            beichengshu -= 0.25
        if self.checkBoxDict["extra_case23"].isChecked():   # 赔偿谅解
            beichengshu -= 0.3
        print("beichengshu",beichengshu)
        LX_bef = jishu * beichengshu

        # 计算罚金
        def fj_get(LX_bef):
            int_part = int(LX_bef)
            dec_part = LX_bef - int_part
            if dec_part <= 0.2:
                return int_part * 2000
            elif 0.2< dec_part <= 0.4:
                return int_part * 2000 + 500
            elif 0.4 < dec_part <= 0.6:
                return (int_part + 0.5) * 2000
            elif 0.6 < dec_part <= 0.8:
                return (int_part + 0.5) * 2000 + 500
            else:
                return (int_part + 1) * 2000

        fj = int(fj_get(LX_bef))

        # 转化数字为刑期
        if LX_bef <= 1.2:
            LX_aft = "1个月"
        elif LX_bef <=1.4:
            LX_aft = "1个月10天"
        elif LX_bef <=1.6:
            LX_aft = "1个月15天"
        elif LX_bef <=1.8:
            LX_aft = "1个月20天"
        elif LX_bef <=2.2:
            LX_aft = "2个月"
        elif LX_bef <=2.4:
            LX_aft = "2个月10天"
        elif LX_bef <=2.6:
            LX_aft = "2个月15天"
        elif LX_bef <=2.8:
            LX_aft = "2个月20天"
        elif LX_bef <=3.2:
            LX_aft = "3个月"
        elif LX_bef <=3.4:
            LX_aft = "3个月10天"
        elif LX_bef <=3.6:
            LX_aft = "3个月15天"
        elif LX_bef <=3.8:
            LX_aft = "3个月20天"
        elif LX_bef <=4.2:
            LX_aft = "4个月"
        elif LX_bef <=4.4:
            LX_aft = "4个月10天"
        elif LX_bef <=4.6:
            LX_aft = "4个月15天"
        elif LX_bef <=4.8:
            LX_aft = "4个月20天"
        elif LX_bef <=5.2:
            LX_aft = "5个月"
        elif LX_bef <=5.4:
            LX_aft = "5个月10天"
        elif LX_bef <=5.6:
            LX_aft = "5个月15天"
        elif LX_bef <=5.8:
            LX_aft = "5个月20天"
        elif LX_bef >5.8:
            LX_aft = "6个月，确定还是危险驾驶吗？"   

        # 缓刑
        if LX_bef <= 1.4:
            hx = 2
        elif LX_bef < 2:
            hx = 3
        elif 2 < LX_bef <= 2.6:
            hx = 4
        elif 2.6 < LX_bef <= 3.2:
            hx = 5
        elif 3.2 < LX_bef <= 3.8:
            hx = 6
        elif 3.8 < LX_bef <= 4.4:
            hx = 7
        elif 4.4 < LX_bef <= 5:
            hx = 8

        # 不起诉
        for num in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,24,25]:     
            if not self.checkBoxDict[f"extra_case{num}"].isChecked():
                if jjhl <= 150:
                    bqs = 1
                else:
                    pass
            else:
                pass
        
        if jjhl < 80 or jjhl > 500:
            self.msginfo("报错：您未输入酒精含量或输入的酒精含量明显错误，请检查后重新输入。")
        else:
            if shixing == 1:
                self.msginfo(">>>建议量刑：处拘役" + LX_aft + "，并处罚金" + str(fj) + "元<<<\n注意：因其"+ sx_reason.rstrip("、") + "，故不适用缓刑！"+"\n计算参考值："+str(LX_bef))
            else:
                if bqs == 1:
                    self.msginfo(">>>建议量刑：其酒精含量较低，且没有额外情节，故建议做相对不起诉处理<<<")
                else:
                    self.msginfo(">>>建议量刑：处拘役" + LX_aft+ "，缓刑" + str(hx) +"个月，并处罚金" + str(fj) + "元。<<<\n  因无禁止缓刑项" + "，故可考虑适用缓刑。"+"\n计算参考值："+str(LX_bef))
    
    # 加粗
    def toggleFontBold(self):
        checkBox = self.sender()
        font = checkBox.font()
        font.setBold(checkBox.isChecked())
        checkBox.setFont(font)

    # 关联
    def onCheckboxchanged(self):
        checkBox = self.sender()
        if checkBox.isChecked():
            # 仅处理
            otherCheckBox = self.checkBoxDict["extra_case22"] if checkBox is self.checkBoxDict["extra_case23"] else self.checkBoxDict["extra_case23"]
            otherCheckBox.setChecked(False)
    def onCheckboxchanged2(self):
        checkBox = self.sender()
        if checkBox.isChecked():
            # 仅处理
            otherCheckBox = self.checkBoxDict["extra_case18"] if checkBox is self.checkBoxDict["extra_case19"] else self.checkBoxDict["extra_case19"]
            otherCheckBox.setChecked(False)
    def onCheckboxchanged3(self):
        checkBox = self.sender()
        if checkBox.isChecked():
            # 仅处理
            otherCheckBox = self.checkBoxDict["extra_case14"] if checkBox is self.checkBoxDict["extra_case24"] else self.checkBoxDict["extra_case24"]
            otherCheckBox.setChecked(False)
    # 弹窗
    def msginfo(self, info):
        msgBox = QMessageBox(self)
        # msgBox.setIcon(QMessageBox.information)
        msgBox.setText(info)
        msgBox.setWindowTitle("计算结果")
        # msgBox.setStandardButtons(QMessageBox.OK)

        msgBox.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())
