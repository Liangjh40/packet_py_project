# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/5
@Author  : Liangjh
@File    : Window.py
@Description:
"""
import os
import subprocess
import sys
import threading

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from Src.mainWindow import Ui_MainWindow
from Src.manager.SignalManager import signal_manager
from Src.manager.configManager import config_manager
from Src.manager.encryptManager import encrypt_manager
from Src.manager.nuitkaManager import nuitka_manager
from Src.manager.unZipManager import un_zip_manager
from Src.manager.zipManager import zip_manager


class EmittingStream(QObject):
    text_written = pyqtSignal(str, QColor)  # 添加颜色参数

    def __init__(self, color=None):
        super().__init__()
        self.color = color or QColor("black")

    def write(self, text):
        self.text_written.emit(text, self.color)

    def flush(self):
        pass


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.init_slot()
        self.display_env()
        self.rb_zip.setChecked(True)
        # # 重定向标准输出
        # self.redirect_console()

    def redirect_console(self):
        # 创建两个独立流对象
        self.stdout_stream = EmittingStream(QColor("black"))
        self.stderr_stream = EmittingStream(QColor("red"))

        # 连接不同信号
        self.stdout_stream.text_written.connect(self.update_text)
        self.stderr_stream.text_written.connect(self.update_text)

        # 分别重定向标准输出和错误
        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

    def update_text(self, text, color):
        # 创建文本格式
        format = QTextCharFormat()
        format.setForeground(color)

        # 获取光标并应用格式
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text, format)

        # # 自动滚动
        # self.text_edit.ensureCursorVisible()

    def init_slot(self):
        self.pb_add_env.clicked.connect(self.add_env)  # 添加环境
        self.pb_del_env.clicked.connect(self.delete_env)  # 删除环境
        self.pb_pj_file.clicked.connect(self.open_pj_file)  # 打开工程文件
        self.pb_pj_ico.clicked.connect(self.open_pj_icon)  # 打开工程图标
        self.pb_pj_dirs.clicked.connect(self.need_copy_dirs)  # 选择要复制的文件夹
        self.pb_pj_save_dirs.clicked.connect(self.save_copy_dirs)  # 保存要复制的文件夹
        self.pb_del_pj.clicked.connect(self.delete_pj)  # 删除工程
        self.pb_start.clicked.connect(self.start_packet)  # 启动打包
        self.pb_encrypt.clicked.connect(self.encrypt_file)  # 启动编译
        signal_manager.updateProgressBarValueSignal.connect(self.update_progress_bar)  # 更新进度条
        signal_manager.messageBoxSignal.connect(self.message_box)  # 弹窗
        self.listWidget.currentItemChanged.connect(self.change_item)  # 点击打包页工程项目
        self.listWidget_2.currentItemChanged.connect(self.change_item)  # 点击打包页环境
        self.listWidget_3.currentItemChanged.connect(self.change_item)  # 点击切换过程方便更改图标和打包复制文件夹

        self.pb_add_skip.clicked.connect(self.add_skip_dirs)  # 添加跳过文件
        self.pb_del_skip.clicked.connect(self.delete_skip_dirs)  # 删除跳过文件

        self.pb_refresh_modify_file.clicked.connect(self.refresh_modifed_files)  # 刷新修改文件
        self.pb_part_encrypt.clicked.connect(self.part_encrypt)  # 编译部分文件
        signal_manager.updatePartEncryptTextSignal.connect(self.update_part_encrypt_text)  # 更新编译文件信息

    def open_pj_file(self):
        defalut_path = "D://"
        pj_name = self.lineEdit.text()
        # print('选择的文件：', pj_name)
        if pj_name:
            if pj_name in config_manager.project_dict.keys():
                if 'path' in config_manager.project_dict[pj_name].keys():
                    defalut_path = os.path.dirname(config_manager.project_dict[pj_name]['path'])
        file_path, _ = QFileDialog.getOpenFileName(self, "打开工程文件", defalut_path, "工程文件(*.py)")
        if file_path:
            print('选择的文件路径为：', file_path)
            pj_name = file_path.split('/')[-1].split('.')[0]
            self.lineEdit.setText(pj_name)
            if pj_name in config_manager.project_dict.keys():
                config_manager.project_dict[pj_name]['path'] = file_path
                config_manager.update_project()
                self.display_env()
            else:
                config_manager.project_dict[pj_name] = {'path': file_path, 'icon': ''}
                config_manager.update_project()

    def open_pj_icon(self):
        defalut_path = "D://"
        pj_name = self.lineEdit.text()
        if pj_name:
            if pj_name in config_manager.project_dict.keys():
                if 'path' in config_manager.project_dict[pj_name].keys():
                    defalut_path = os.path.dirname(config_manager.project_dict[pj_name]['path'])
        file_path, _ = QFileDialog.getOpenFileName(self, "打开工程图标", defalut_path, "")
        if file_path:
            print('选择的图标路径为：', file_path)
            pj_name = self.lineEdit.text()
            if pj_name in config_manager.project_dict.keys():
                config_manager.project_dict[pj_name]['icon'] = file_path
                config_manager.update_project()

            else:
                # messageBox弹窗提示
                QMessageBox.warning(self, "提示", "请先添加工程主文件", QMessageBox.Yes)
            self.display_env()

    def need_copy_dirs(self):
        defalut_path = "D://"
        pj_name = self.lineEdit.text()
        if pj_name:
            if pj_name in config_manager.project_dict.keys():
                if 'path' in config_manager.project_dict[pj_name].keys():
                    defalut_path = os.path.dirname(config_manager.project_dict[pj_name]['path'])
        file_path = QFileDialog.getExistingDirectory(self, "选择要复制的文件夹", defalut_path)
        if file_path:
            dir_name = os.path.basename(file_path)
            print('选择的文件夹路径为：', dir_name)
            dirs = self.lineEdit_2.text()
            if dirs:
                self.lineEdit_2.setText(dirs + ';' + dir_name)
            else:
                self.lineEdit_2.setText(dir_name)
            print('lineEdit_2：', self.lineEdit_2.text())

    def save_copy_dirs(self):
        pj_name = self.lineEdit.text()
        dirs = self.lineEdit_2.text()
        if not dirs:
            QMessageBox.warning(self, "提示", "请先选择要复制的文件夹", QMessageBox.Yes)
            return
        dirs_list = dirs.split(';')
        if not pj_name:
            QMessageBox.warning(self, "提示", "请先添加工程主文件", QMessageBox.Yes)
            return

        config_manager.project_dict[pj_name]['copy_dirs'] = dirs_list
        print(f"项目：{pj_name}, 要复制的文件夹：{config_manager.project_dict[pj_name]['copy_dirs']}")
        config_manager.update_project()
        QMessageBox.information(self, "提示", "保存成功", QMessageBox.Yes)

    def change_item(self):
        sender = self.sender().objectName()
        print('sender:', sender)
        if sender == 'listWidget':
            currentItem = self.sender().currentItem().text().split('（')[0]
            print('切换的工程为：', currentItem)
            self.label_5.setText(currentItem)
            self.label_9.setText(currentItem)
            self.show_skip_dirs()
        elif sender == 'listWidget_2':
            currentItem = self.sender().currentItem().text()
            print('切换的环境为：', currentItem)
            self.label_7.setText(currentItem)
            self.label_11.setText(currentItem)
        elif sender == 'listWidget_3':
            currentItem = self.listWidget_3.currentItem().text().split('（')[0]
            print('切换的工程为：', currentItem)
            if currentItem in config_manager.project_dict.keys():
                if 'copy_dirs' in config_manager.project_dict[currentItem].keys():
                    self.lineEdit_2.setText(';'.join(config_manager.project_dict[currentItem]['copy_dirs']))
                else:
                    self.lineEdit_2.setText('')
                self.lineEdit.setText(currentItem)

    def delete_pj(self):
        currentItem = self.listWidget_3.currentItem().text().split('（')[0]

        print('删除的工程为：', currentItem)
        config_manager.project_dict.pop(currentItem)
        config_manager.update_project()
        self.display_env()

    def display_env(self):
        self.listWidget.clear()
        self.listWidget_2.clear()
        self.listWidget_3.clear()
        self.listWidget_4.clear()
        for key in config_manager.env_dict.keys():
            self.listWidget_2.addItem(key)
            self.listWidget_4.addItem(key)
        for key in config_manager.project_dict.keys():
            key_name = key
            if config_manager.project_dict[key]['icon']:
                key_name = key + '（已设置图标）'
            else:
                key_name = key + '（未设置图标）'
            self.listWidget.addItem(key_name)
            self.listWidget_3.addItem(key_name)

    def add_env(self):
        # 打开文件夹选择对话框 只能选择文件夹
        file_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "D://conda/envs")
        if file_path:
            print('选择的文件夹路径为：', file_path)

            zip_name = file_path.split('/')[-1] + '.zip'

            signal_manager.updateProgressBarValueSignal.emit(0)
            zip_manager.target_zip_name = zip_name
            zip_manager.src_path = file_path
            zip_manager.zip_folders_and_files()
            local_env_path = os.path.join(config_manager.work_path, 'PyZip', zip_name)
            if zip_name in config_manager.env_dict.keys():

                config_manager.env_dict[zip_name]['zip_path'] = local_env_path
                config_manager.env_dict[zip_name]['local_env_path'] = file_path
            else:
                config_manager.env_dict[zip_name] = {'zip_path': local_env_path, 'local_env_path': file_path}
            config_manager.update_env()
            self.display_env()

    def delete_env(self):
        currentItem = self.listWidget_4.currentItem().text()
        print('删除的环境为：', currentItem)
        config_manager.env_dict.pop(currentItem)
        config_manager.update_env()
        # 删除文件夹里的压缩包
        file_path = config_manager.work_path + r"\PyZip" + r"\{}".format(currentItem)
        try:
            # 检查文件是否存在
            if os.path.isfile(file_path):
                os.remove(file_path)  # 删除文件
                print(f"成功删除文件: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        except Exception as e:
            print(f"删除文件时出错: {e}")
        self.display_env()

    def update_progress_bar(self, value):
        self.progressBar.setValue(value)
        self.progressBar_packet.setValue(value)

    def message_box(self, message):
        QMessageBox.warning(self, "提示", message, QMessageBox.Yes)

    def start_packet(self):
        self.task = threading.Thread(target=self.packet_thread)
        self.task.daemon = True
        self.task.start()

    def packet_thread(self):
        try:
            current_project = self.listWidget.currentItem().text()
            current_project = current_project.split('（')[0]
            current_env = self.listWidget_2.currentItem().text()
        except AttributeError as e:
            signal_manager.messageBoxSignal.emit("请先选择工程和环境")
            print("中止打包")
            return

        # 生成可执行文件
        signal_manager.updateProgressBarValueSignal.emit(0)
        nuitka_manager.update_project_path(current_project)
        nuitka_manager.update_nuitka_path(current_env)
        # nuitka_manager.update_nuitka_path('explorer38.zip')
        nuitka_manager.packing_project()
        signal_manager.updateProgressBarValueSignal.emit(10)

        # 复制源代码
        encrypt_manager.update_main_path(current_project)
        encrypt_manager.update_env_path(current_env)
        encrypt_manager.copy_dir()
        encrypt_manager.delete_ui_file()
        # # encrypt_manager.encrypt_file()
        signal_manager.updateProgressBarValueSignal.emit(50)
        # 解压环境
        if self.rb_zip.isChecked():
            un_zip_manager.update_zip_path(config_manager.env_dict[current_env]['zip_path'])  # 存放压缩包的路径
            un_zip_manager.update_dest_path(encrypt_manager.dst_path)  # 解压到打包后的目录
            un_zip_manager.un_zip()

        signal_manager.updateProgressBarValueSignal.emit(100)

    def encrypt_file(self):
        print("encrypt_file:")
        try:
            current_project = self.listWidget.currentItem().text()
            current_project = current_project.split('（')[0]
            current_env = self.listWidget_2.currentItem().text()
        except AttributeError as e:
            signal_manager.messageBoxSignal.emit("请先选择工程和环境")
            print("中止打包")
            return

        encrypt_manager.update_main_path(current_project)
        encrypt_manager.update_env_path(current_env)
        encrypt_manager.encrypt_file()

    def show_skip_dirs(self):
        pj_name = self.label_5.text()
        skip_dirs = config_manager.project_dict[pj_name].get('skip_dirs', [])
        self.listWidget_5.clear()
        for dir_name in skip_dirs:
            self.listWidget_5.addItem(dir_name)

    def add_skip_dirs(self):
        pj_name = self.label_5.text()
        env_name = self.label_7.text()
        if not pj_name:
            QMessageBox.warning(self, "提示", "请先选择工程", QMessageBox.Yes)
            return
        if not env_name:
            QMessageBox.warning(self, "提示", "请先选择环境", QMessageBox.Yes)
            return
        defalut_path = "D://"
        print(f'工程的cinfig为：{config_manager.project_dict.keys()}, 项目名字为：{pj_name}')
        pj_list = list(config_manager.project_dict.keys())
        if pj_name in pj_list:
            if 'path' in config_manager.project_dict[pj_name].keys():
                pj_path = os.path.dirname(config_manager.project_dict[pj_name]['path'])
                defalut_path = os.path.join(pj_path, 'dist', f'{pj_name}')
                print(f'项目的路径为：{defalut_path}')
        if defalut_path == "D://" or not os.path.exists(defalut_path):
            QMessageBox.warning(self, "提示", "未找到打包路径，请先打包", QMessageBox.Yes)
            return
        file_path = QFileDialog.getExistingDirectory(self, "选择要复制的文件夹", defalut_path)
        if file_path:
            dir_name = os.path.basename(file_path)
            print('选择的文件夹路径为：', dir_name)
            skip_dirs = config_manager.project_dict[pj_name].get('skip_dirs', [])
            if dir_name not in skip_dirs:
                skip_dirs.append(dir_name)
                config_manager.project_dict[pj_name]['skip_dirs'] = skip_dirs
                config_manager.update_project()
                self.show_skip_dirs()
                print('跳过的文件夹：', skip_dirs)

    def delete_skip_dirs(self):
        pj_name = self.label_5.text()
        skip_dirs = config_manager.project_dict[pj_name].get('skip_dirs', [])
        selected_item = self.listWidget_5.currentItem().text()
        if selected_item in skip_dirs:
            skip_dirs.remove(selected_item)
            config_manager.project_dict[pj_name]['skip_dirs'] = skip_dirs
            config_manager.update_project()
            self.show_skip_dirs()
            print(f"删除的跳过文件夹：{selected_item}")

    """
    部分编译
    """

    def refresh_modifed_files(self):
        pj_name = self.label_9.text()
        pj_env = self.label_11.text()
        if not pj_name:
            QMessageBox.warning(self, "提示", "请先选择工程", QMessageBox.Yes)
            return
        if not pj_env:
            QMessageBox.warning(self, "提示", "请先选择环境", QMessageBox.Yes)
            return
        pj_path = os.path.dirname(config_manager.project_dict[pj_name]['path'])
        blue_files = self.get_modified_unstaged_files(pj_path)
        self.listWidget_6.clear()
        for file in blue_files:
            self.listWidget_6.addItem(file)
        encrypt_manager.part_files = blue_files
        encrypt_manager.update_main_path(pj_name)
        encrypt_manager.update_env_path(pj_env)
        # print("PyCharm中蓝色的修改文件（未暂存）：")
        # for file in blue_files:
        #     print(f"- {file}")

    @staticmethod
    def get_modified_unstaged_files(repo_path=None):
        """
        获取Git仓库中已修改但未暂存的文件（彻底去除哈希值）
        :param repo_path: Git仓库根目录路径（默认当前工作目录）
        :return: 纯净的文件路径列表（无哈希值和冗余信息）
        """
        repo_path = repo_path or os.getcwd()

        try:
            # 配置Git不转义中文
            subprocess.run(
                ["git", "config", "core.quotepath", "false"],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                check=False
            )

            # 执行Git命令获取状态
            result = subprocess.run(
                ["git", "status", "--porcelain=v2"],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                check=True
            )

            modified_files = []
            for line in result.stdout.splitlines():
                if line.startswith('?'):  # 跳过未跟踪文件
                    continue

                parts = line.split()
                if len(parts) < 8:  # 确保字段足够（至少包含到文件名的起始位置）
                    continue

                # 筛选"已修改未暂存"的文件（前缀=1，状态含"M"）
                status_prefix = parts[0]
                status = parts[1]
                if status_prefix == "1" and 'M' in status:
                    # 关键修正：文件名从第8个字段开始（跳过前缀、状态、模式、2个哈希值）
                    filename_raw = ' '.join(parts[8:])
                    # 确保中文正常显示
                    try:
                        filename = filename_raw
                        filename.encode('utf-8')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        filename = filename_raw.encode('latin-1').decode('utf-8', errors='replace')
                    modified_files.append(filename)
                    # print(f"已修改未暂存的文件：{filename}")
            return modified_files

        except subprocess.CalledProcessError as e:
            print(f"Git命令执行失败：{e.stderr}")
            return []
        except Exception as e:
            print(f"获取文件列表失败：{str(e)}")
            return []



    def part_encrypt(self):
        self.textEdit.clear()
        encrypt_manager.encrypt_file()
        # import threading
        # self.task = threading.Thread(target=encrypt_manager.part_encrypt_file)
        # self.task.daemon = True
        # self.task.start()


    def update_part_encrypt_text(self, text, status):
        # 状态与颜色映射：error-红，info-绿，warning-黄
        color_map = {
            "error": QColor(200, 0, 0),  # 深红色（RGB: 200,0,0）
            "info": QColor(0, 160, 0),  # 深绿色（RGB: 0,160,0）
            "warning": QColor(255, 165, 0)  # 橙色（RGB: 255,165,0，比纯黄暗）

            # 也可使用Qt预定义颜色（二选一即可）：
            # "error": Qt.red,
            # "info": Qt.yellow,
            # "warning": Qt.green
        }

        # 获取当前状态对应的颜色，无效状态默认黑色
        color = color_map.get(status, QColor(0, 0, 0))

        # 创建格式并应用颜色
        format = QTextCharFormat()
        format.setForeground(color)
        # 设置字体大小（如12pt，可根据需求调整，建议10-14pt）
        if status == "info":
            format.setFontPointSize(10)  # 字体大小从默认（通常10pt）增大到12pt
        else:
            format.setFontPointSize(12)  # 字体大小从默认（通常10pt）增大到12pt

        # 插入文本
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text+'\n', format)
