import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
import zipfile
import fitz
import re
import WXJS_newPdfget
import os

global file_load
file_load = os.getcwd()


class NewQLineEdit(QtWidgets.QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        self.label.setPixmap(QtGui.QPixmap(file_load + r'\image\背景图.png'))
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
        self.label_4.setGeometry(QtCore.QRect(560, 310, 651, 180))
        self.label_4.setStyleSheet("color: gray")

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
        self.pushButton_2.setGeometry(QtCore.QRect(260, 350, 161, 40))
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
        self.pushButton_3.setGeometry(QtCore.QRect(180, 350, 61, 41))
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
        self.pushButton_3.setText("调整")
        self.pushButton_3.clicked.connect(self.change_LX)  # 打开调整窗口

        # 设置进度条
        self.progressBar = QtWidgets.QProgressBar(self)
        # self.progressBar.setGeometry(QtCore.QRect(40, 400, 632, 10))
        self.progressBar.setGeometry(QtCore.QRect(260, 392, 192, 10))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        # 设置下拉按钮
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(250, 115, 151, 38))
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("未传入")
        self.comboBox.addItem("识别失败")
        self.comboBox.addItem("危险驾驶")
        self.comboBox.addItem("交通肇事")
        self.comboBox.addItem("开设赌场")
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
        self.label_2.setText("请拖压缩包到此：")
        self.label_2.setObjectName("label_2")
        font = QtGui.QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setText("待传入")
        self.label_3.setObjectName("label_3")
        font = QtGui.QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setText("危险驾驶版")
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
        print('调试信息：进入exTractFiles函数')
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
        self.comboBox.setCurrentIndex(2)  # 下拉框设置为危险驾驶

        zip_file = zipfile.ZipFile(self.zip_file_path)
        dest_folder = os.path.join(os.path.dirname(self.zip_file_path),
                                   os.path.splitext(os.path.basename(self.zip_file_path))[0])

        pdf_files = []
        for name in zip_file.namelist():
            print("调试信息：进入for name in zip_file.namelist()")
            if name.endswith(".pdf"):
                zip_file.extract(name, dest_folder)
                pdf_files.append(os.path.join(dest_folder, name))

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
            print("调试信息：成功打开output")
            file.write(combined_text)
        # 关闭文档
        doc.close()
        # 删除pdf文件夹
        # shutil.rmtree(dest_folder)
        print("调试信息：成功走到这一步")
        LX_result = WXJS_newPdfget.LX("output.txt")
        # print('调试信息：LX_result', LX_result)
        self.label_3.setText(LX_result)
        if LX_result.find("不起诉处理") != -1:
            LX_final = LX_result[LX_result.find("建议量刑："):(LX_result.find("处理") + 2)]
        else:
            LX_final = LX_result[LX_result.find("建议量刑："):(LX_result.find("元") + 1)]

        # 把量刑结果写入txt
        txt_load = file_load + "/模板/LX_change.txt"
        with open(txt_load, "w", encoding="gbk") as txt_file:
            txt_file.write(LX_final)
        print('调试信息：LX_final写入LX_change成功')

    def on_pushButton_2_clicked(self):
        # 修改量刑
        text_2 = self.label_3.text()
        if text_2.startswith("建议量刑"):
            try:
                with open(file_load + "/模板/LX_change.txt", "w", encoding='gbk') as LX_file:
                    LX_file.write(text_2)
            except:
                pass
        else:
            pass

        self.progressBar.setValue(15)  # 进度条10%
        try:
            import WXJS_Pdfget
            self.progressBar.setValue(60)  # 进度条20%
            WXJS_Pdfget.SC('output.txt')
            self.progressBar.setValue(65)  # 进度条50%
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
        text_get = self.label_3.text()
        if text_get.find("不起诉处理") != -1:
            text = '建议量刑：可考虑做不起诉处理'
        else:
            start_LX = text_get.find('建议量刑')
            end_LX = text_get.find('元')
            text = text_get[start_LX:end_LX] + '元'
        self.second_window = SecondWindow(text)
        self.second_window.exec_()
        self.label_3.setText(self.second_window.text_edit.toPlainText())


class SecondWindow(QDialog):
    def __init__(self, text):
        super().__init__()

        self.text_edit = QTextEdit(text)
        self.setWindowTitle('调整量刑')
        font = QFont("Microsoft Yahei", 15)
        self.setFont(font)

        self.button = QPushButton('确认修改')
        self.button.clicked.connect(self.update_label)

        layout = QGridLayout()
        layout.addWidget(self.text_edit, 0, 0)
        layout.addWidget(self.button, 1, 0)
        self.setLayout(layout)

    def update_label(self):
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())
