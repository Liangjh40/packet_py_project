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

from PyQt5.QtCore import QObject, pyqtSignal, Qt, QPoint, QEvent, QUrl
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor, QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QWidget, QAbstractItemView, QListView, QTreeView

from Src.mainWindow import Ui_MainWindow
from Src.manager.SignalManager import signal_manager
from Src.manager.configManager import config_manager
from Src.manager.encryptManager import encrypt_manager
from Src.manager.nuitkaManager import nuitka_manager
from Src.manager.unZipManager import un_zip_manager
from Src.manager.zipManager import zip_manager
from Src.style import get_stylesheet





class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.m_drag = False
        self.m_DragPosition = QPoint()
        self.m_DragPosition = QPoint()
        self.setStyleSheet(get_stylesheet())
        self.init_slot()
        self.init_title_bar()
        self.menubar.installEventFilter(self)
        self.display_env()
        self.rb_zip.setChecked(True)


    def init_title_bar(self):
        # 创建容器组件
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(0)

        # 最小化
        self.btn_min = QPushButton("－")
        self.btn_min.setToolTip("最小化")
        self.btn_min.clicked.connect(self.showMinimized)
        corner_layout.addWidget(self.btn_min)

        # 最大化/还原
        self.btn_max = QPushButton("□")
        self.btn_max.setToolTip("最大化")
        self.btn_max.clicked.connect(self.toggle_maximized)
        corner_layout.addWidget(self.btn_max)

        # 关闭
        self.btn_close = QPushButton("×")
        self.btn_close.setToolTip("关闭")
        self.btn_close.clicked.connect(self.close)
        corner_layout.addWidget(self.btn_close)

        # 设置一些基本样式
        for btn in [self.btn_min, self.btn_max, self.btn_close]:
            btn.setFixedSize(60, 40)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    font-family: "Microsoft YaHei";
                    font-size: 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
        # 单独设置关闭按钮的hover样式
        self.btn_close.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-family: "Microsoft YaHei";
                font-size: 26px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)

        # 设置为菜单栏的角落组件
        self.menubar.setCornerWidget(corner_widget, Qt.TopRightCorner)

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_max.setText("□")
            self.btn_max.setToolTip("最大化")
        else:
            self.showMaximized()
            self.btn_max.setText("❐")
            self.btn_max.setToolTip("还原")


    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_drag:
            self.move(event.globalPos() - self.m_DragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False

    def eventFilter(self, obj, event):
        if obj == self.menubar:
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    # 检查是否点击在菜单项上
                    if not self.menubar.actionAt(event.pos()):
                        self.m_drag = True
                        self.m_DragPosition = event.globalPos() - self.pos()
                        return True  # 消费事件
            elif event.type() == QEvent.MouseMove:
                if self.m_drag and (event.buttons() & Qt.LeftButton):
                    self.move(event.globalPos() - self.m_DragPosition)
                    return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.m_drag = False
        return super().eventFilter(obj, event)




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
        signal_manager.updateProgressBarRangeSignal.connect(self.update_progress_bar_range)  # 进度条范围
        signal_manager.messageBoxSignal.connect(self.message_box)  # 弹窗
        self.listWidget.currentItemChanged.connect(self.change_item)  # 点击打包页工程项目
        self.listWidget_2.currentItemChanged.connect(self.change_item)  # 点击打包页环境
        self.listWidget_3.currentItemChanged.connect(self.change_item)  # 点击切换过程方便更改图标和打包复制文件夹

        self.pb_add_skip.clicked.connect(self.add_skip_files)  # 添加跳过文件
        self.pb_add_skip_dir.clicked.connect(self.add_skip_dirs)  # 添加跳过文件夹
        self.pb_del_skip.clicked.connect(self.delete_skip_dirs)  # 删除跳过文件

        self.pb_refresh_modify_file.clicked.connect(self.refresh_modifed_files)  # 刷新修改文件
        self.pb_part_encrypt.clicked.connect(self.part_encrypt)  # 编译部分文件
        signal_manager.updatePartEncryptTextSignal.connect(self.update_part_encrypt_text)  # 更新编译文件信息
        signal_manager.updateFullEncryptTextSignal.connect(self.update_full_encrypt_text)  # 更新全量编译信息

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
            # 自动获取项目名称
            pj_name = file_path.split('/')[-1].split('.')[0]
            self.lineEdit.setText(pj_name)
            if pj_name in config_manager.project_dict.keys():
                config_manager.project_dict[pj_name]['path'] = file_path
                config_manager.update_project()
                self.display_env()
            else:
                config_manager.project_dict[pj_name] = {'path': file_path, 'icon': ''}
                config_manager.update_project()
                self.display_env()

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
            item = self.sender().currentItem()
            if not item: return
            currentItem = item.text().split('（')[0]
            print('切换的工程为：', currentItem)
            self.label_5.setText(currentItem)
            self.label_9.setText(currentItem)
            self.show_skip_dirs()
        elif sender == 'listWidget_2':
            item = self.sender().currentItem()
            if not item: return
            currentItem = item.text()
            print('切换的环境为：', currentItem)
            self.label_7.setText(currentItem)
            self.label_11.setText(currentItem)
        elif sender == 'listWidget_3':
            item = self.listWidget_3.currentItem()
            if not item: return
            currentItem = item.text().split('（')[0]
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
        """添加conda环境，使用conda-pack进行打包"""
        from PyQt5.QtWidgets import QInputDialog

        # 获取所有可用的conda环境列表
        try:
            result = subprocess.run(
                ["conda", "env", "list"],
                capture_output=True,
                text=True,
                check=True
            )

            # 解析conda环境列表
            env_lines = result.stdout.strip().split('\n')
            env_list = []
            env_map = {}
            for line in env_lines:
                if line and not line.startswith('#'):
                    parts = line.split()
                    if parts:
                        env_name = parts[0]
                        if env_name:
                            env_list.append(env_name)
                        for part in parts[1:]:
                            if os.path.isdir(part):
                                env_map[env_name] = part
                                break

            if not env_list:
                QMessageBox.warning(self, "提示", "未找到conda环境", QMessageBox.Yes)
                return

        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "提示", f"获取conda环境列表失败：{e}", QMessageBox.Yes)
            return
        except FileNotFoundError:
            QMessageBox.warning(self, "提示", "未找到conda命令，请确保已安装Anaconda/Miniconda", QMessageBox.Yes)
            return

        # 弹出对话框让用户选择环境
        env_name, ok = QInputDialog.getItem(
            self,
            "选择conda环境",
            "请选择要打包的环境：",
            env_list,
            0,
            False
        )

        if not ok or not env_name:
            return

        print(f'选择的环境名称：{env_name}')
        env_path = env_map.get(env_name)

        # 检查当前环境中是否安装了conda-pack（查找conda-pack可执行文件）
        conda_pack_exe = os.path.join(os.path.dirname(sys.executable), "Scripts", "conda-pack.exe")
        if not os.path.exists(conda_pack_exe):
            QMessageBox.warning(
                self,
                "提示",
                f"当前环境中未安装conda-pack！\n未找到文件：{conda_pack_exe}\n请在Tools环境中安装：\npip install conda-pack",
                QMessageBox.Yes
            )
            return

        # 在后台线程中执行打包
        signal_manager.updateProgressBarValueSignal.emit(0)
        self.task = threading.Thread(target=self.add_env_thread, args=(env_name, env_path, conda_pack_exe))
        self.task.daemon = True
        self.task.start()

    def add_env_thread(self, env_name, env_path, conda_pack_exe):
        """后台线程：执行conda-pack打包"""
        import shutil
        from pathlib import Path
        import tarfile

        def conda_pack_supports_flag(flag):
            try:
                help_result = subprocess.run(
                    [conda_pack_exe, "--help"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                return flag in help_result.stdout
            except Exception:
                return False
        
        def resolve_conda_exe():
            candidates = []
            env_conda_exe = os.environ.get("CONDA_EXE")
            if env_conda_exe:
                candidates.append(env_conda_exe.strip('"'))
            try:
                conda_root = Path(conda_pack_exe).resolve().parents[3]
                candidates.append(str(conda_root / "Scripts" / "conda.exe"))
            except Exception:
                pass
            for exe_name in ("conda.exe", "conda"):
                exe_path = shutil.which(exe_name)
                if exe_path:
                    candidates.append(exe_path)
            for candidate in candidates:
                if candidate and os.path.isfile(candidate):
                    return candidate
            return None
        
        def pack_selected_env(prefix_path, output_path):
            include_dirs = ['DLLs', 'include', 'Lib', 'Scripts', 'tcl', 'Library']
            include_files = ['python.exe', 'python3.dll']
            if os.path.exists(output_path):
                os.remove(output_path)
            try:
                tar = tarfile.open(output_path, "w:gz", compresslevel=1)
            except TypeError:
                tar = tarfile.open(output_path, "w:gz")
            with tar:
                for name in include_dirs:
                    src = os.path.join(prefix_path, name)
                    if not os.path.isdir(src):
                        print(f"跳过缺失目录: {src}")
                        continue
                    tar.add(src, arcname=os.path.relpath(src, prefix_path))
                for name in include_files:
                    src = os.path.join(prefix_path, name)
                    if not os.path.isfile(src):
                        print(f"跳过缺失文件: {src}")
                        continue
                    tar.add(src, arcname=os.path.relpath(src, prefix_path))

        # 设置输出文件路径
        output_filename = f"{env_name}.tar.gz"
        final_output_dir = os.path.join(config_manager.work_path, 'PyZip')
        final_output_path = os.path.join(final_output_dir, output_filename)

        # 确保PyZip目录存在
        os.makedirs(final_output_dir, exist_ok=True)

        # 显示进度
        signal_manager.updateProgressBarValueSignal.emit(10)
        signal_manager.updateProgressBarRangeSignal.emit(0, 0)
  
        try:
            if env_path and os.path.isdir(env_path):
                print(f"使用自定义精简打包: {env_path}")
                pack_selected_env(env_path, final_output_path)
            else:
                # 构建conda pack命令（使用当前Python环境的conda-pack）
                cmd = [conda_pack_exe]
                cmd.extend(["-n", env_name])
                cmd.extend([
                    "--exclude", "*.pyc",
                    "--exclude", "*.pyo",
                    "--exclude", "*.a",
                    "--exclude", "Lib/site-packages/*/tests",
                    "--exclude", "Lib/site-packages/*/test",
                    "--exclude", "Lib/site-packages/*/docs",
                    "--exclude", "Lib/site-packages/*/__pycache__",
                    "--exclude", "pkgs/*",
                    "--exclude", "*.dist-info/RECORD",
                    "-o", final_output_path
                ])
                if conda_pack_supports_flag("--compress-level"):
                    cmd.extend(["--compress-level", "1"])
                # 执行打包命令
                print(f"执行命令：{' '.join(cmd)}")
                env = os.environ.copy()
                conda_exe = resolve_conda_exe()
                if conda_exe:
                    env["CONDA_EXE"] = conda_exe
                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    env=env
                )

            signal_manager.updateProgressBarValueSignal.emit(80)

            # 检查输出文件并更新配置
            if os.path.exists(final_output_path):
                file_size = os.path.getsize(final_output_path) / (1024 * 1024)  # MB
                print(f"打包完成，文件大小：{file_size:.2f} MB")

                # 更新配置
                if output_filename in config_manager.env_dict.keys():
                    config_manager.env_dict[output_filename]['zip_path'] = final_output_path
                    config_manager.env_dict[output_filename]['env_name'] = env_name
                else:
                    config_manager.env_dict[output_filename] = {
                        'zip_path': final_output_path,
                        'env_name': env_name
                    }

                config_manager.update_env()
                self.display_env()

                signal_manager.updateProgressBarValueSignal.emit(100)
                signal_manager.messageBoxSignal.emit(
                    f"打包完成！\n文件路径：{final_output_path}\n文件大小：{file_size:.2f} MB"
                )
            else:
                signal_manager.updateProgressBarValueSignal.emit(0)
                signal_manager.messageBoxSignal.emit("打包失败：输出文件未生成")

        except subprocess.CalledProcessError as e:
            signal_manager.updateProgressBarValueSignal.emit(0)
            error_msg = f"打包失败：{e.stderr if e.stderr else str(e)}"
            print(error_msg)
            signal_manager.messageBoxSignal.emit(error_msg)
        except Exception as e:
            signal_manager.updateProgressBarValueSignal.emit(0)
            error_msg = f"打包失败：{str(e)}"
            print(error_msg)
            signal_manager.messageBoxSignal.emit(error_msg)
        finally:
            signal_manager.updateProgressBarRangeSignal.emit(0, 100)

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

    def update_progress_bar_range(self, min_value, max_value):
        self.progressBar.setRange(min_value, max_value)
        self.progressBar_packet.setRange(min_value, max_value)

    def message_box(self, message):
        QMessageBox.warning(self, "提示", message, QMessageBox.Yes)

    def start_packet(self):
        # 1. 获取当前选中的项目
        try:
            current_item = self.listWidget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "提示", "请先选择工程", QMessageBox.Yes)
                return
            current_project = current_item.text().split('（')[0]
        except AttributeError:
             QMessageBox.warning(self, "提示", "请先选择工程", QMessageBox.Yes)
             return
        # 若已存在打包目录，提示是否重新打包
        try:
            project_path = config_manager.project_dict[current_project]['path']
            project_dir = os.path.dirname(project_path)
            dist_dir = os.path.join(project_dir, "dist", current_project)
            if os.path.isdir(dist_dir) and os.listdir(dist_dir):
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText(f"检测到已存在打包目录：\n{dist_dir}\n请选择操作：")
                btn_repack = msg_box.addButton("重新打包", QMessageBox.AcceptRole)
                btn_open = msg_box.addButton("打开目录", QMessageBox.ActionRole)
                btn_cancel = msg_box.addButton("取消", QMessageBox.RejectRole)
                msg_box.setDefaultButton(btn_cancel)
                msg_box.exec_()
                clicked = msg_box.clickedButton()
                if clicked == btn_open:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(dist_dir))
                    return
                if clicked != btn_repack:
                    return
        except Exception:
            pass

        # 2. 获取当前选中的 conda 环境
        try:
            current_env_item = self.listWidget_2.currentItem()
            if not current_env_item:
                QMessageBox.warning(self, "提示", "请先选择环境", QMessageBox.Yes)
                return
            # 去除 .tar.gz 后缀获取环境名
            env_name_with_ext = current_env_item.text()
            env_name = env_name_with_ext.replace('.tar.gz', '')
            print(f"选中的环境：{env_name}")
        except AttributeError:
            QMessageBox.warning(self, "提示", "请先选择环境", QMessageBox.Yes)
            return
        
        # 3. 通过 conda env list 查找环境路径
        try:
            result = subprocess.run(
                ["conda", "env", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 解析 conda 环境列表
            conda_env_path = None
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('#'):
                    parts = line.split()
                    if parts and parts[0] == env_name:
                        # 找到匹配的环境
                        if len(parts) >= 2:
                            # 路径可能在索引 1 或更后面（如果有 * 标记）
                            for part in parts[1:]:
                                if os.path.isdir(part):
                                    conda_env_path = part
                                    break
                        break
            
            if not conda_env_path:
                QMessageBox.warning(
                    self, 
                    "提示", 
                    f"未找到 conda 环境 '{env_name}'！\n请确保该环境已安装在本地。",
                    QMessageBox.Yes
                )
                return
            
            print(f"找到 conda 环境路径：{conda_env_path}")
            
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "提示", f"执行 conda env list 失败：{e}", QMessageBox.Yes)
            return
        except FileNotFoundError:
            QMessageBox.warning(self, "提示", "未找到 conda 命令，请确保已安装 Anaconda/Miniconda", QMessageBox.Yes)
            return
        
        # 4. 检查环境中是否有 Nuitka
        nuitka_found = False
        for ext in ["bat", "exe", "cmd"]:
            nuitka_path = os.path.join(conda_env_path, "Scripts", f"nuitka.{ext}")
            if os.path.exists(nuitka_path):
                nuitka_found = True
                break
        
        if not nuitka_found:
            QMessageBox.warning(
                self,
                "提示",
                f"在 conda 环境 '{env_name}' 中未找到 Nuitka！\n环境路径：{conda_env_path}\n请在该环境中安装 Nuitka。",
                QMessageBox.Yes
            )
            return
        
        # 5. 启动打包线程
        self.task = threading.Thread(target=self.packet_thread, args=(current_project, conda_env_path))
        self.task.daemon = True
        self.task.start()

    def packet_thread(self, current_project, conda_env_path):
        # 生成可执行文件
        signal_manager.updateProgressBarValueSignal.emit(0)
        nuitka_manager.update_project_path(current_project)
        nuitka_manager.set_nuitka_path_by_conda_env(conda_env_path)

        nuitka_manager.packing_project()
        signal_manager.updateProgressBarValueSignal.emit(10)

        # 检查是否需要解压环境
        if self.rb_zip.isChecked():
            try:
                # 获取当前选中的环境名（去除 .tar.gz 后缀）
                current_env_item = self.listWidget_2.currentItem()
                if current_env_item:
                    env_name_with_ext = current_env_item.text()
                    env_name = env_name_with_ext.replace('.tar.gz', '')
                    
                    # 从 config 获取环境压缩包路径
                    if env_name_with_ext in config_manager.env_dict:
                        tar_gz_path = config_manager.env_dict[env_name_with_ext]['zip_path']
                        
                        
                        # 计算解压目标路径：项目根目录/dist/{项目名}/
                        project_path = config_manager.project_dict[current_project]['path']
                        project_dir = os.path.dirname(project_path)
                        # 使用项目名作为文件夹名（与 Nuitka 输出一致）
                        dest_path = os.path.join(project_dir, "dist", current_project)
                        
                        print(f"开始解压环境到: {dest_path}")
                        signal_manager.updateProgressBarValueSignal.emit(20)
                        
                        # 调用解压管理器
                        un_zip_manager.unpack_conda_env(tar_gz_path, dest_path)
                        
                        signal_manager.updateProgressBarValueSignal.emit(40)
                        print(f"环境解压完成")
                    else:
                        print(f"警告：未找到环境 {env_name_with_ext} 的配置信息")
            except Exception as e:
                print(f"解压环境时出错：{e}")
                signal_manager.messageBoxSignal.emit(f"解压环境失败：{str(e)}")

        # 复制源代码
        encrypt_manager.update_main_path(current_project)
        encrypt_manager.set_env_path_by_venv(conda_env_path)

        encrypt_manager.copy_dir()
        encrypt_manager.delete_ui_file()
        signal_manager.updateProgressBarValueSignal.emit(50)


        signal_manager.updateProgressBarValueSignal.emit(100)

    def encrypt_file(self):
        print("全量编译启动")
        try:
            current_project = self.listWidget.currentItem().text()
            current_project = current_project.split('（')[0]
            current_env = self.listWidget_2.currentItem().text()
        except AttributeError as e:
            signal_manager.messageBoxSignal.emit("请先选择工程和环境")
            print("中止打包")
            return

        self.text_edit.clear()
        encrypt_manager.update_main_path(current_project)
        encrypt_manager.update_env_path(current_env)
        encrypt_manager.encrypt_file()

    def show_skip_dirs(self):
        pj_name = self.label_5.text()
        project_cfg = config_manager.project_dict[pj_name]
        skip_dirs = project_cfg.get('skip_dirs', [])
        skip_dirs_auto = project_cfg.get('skip_dirs_auto', True)
        # 若未设置跳过文件夹，或仍处于自动模式，则使用环境精简打包的目录清单
        if not skip_dirs or skip_dirs_auto:
            default_dirs = list(getattr(zip_manager, "folder_to_zip", []))
            if default_dirs:
                project_cfg['skip_dirs'] = default_dirs
                project_cfg['skip_dirs_auto'] = True
                config_manager.update_project()
                skip_dirs = default_dirs
        self.listWidget_5.clear()
        for dir_name in skip_dirs:
            self.listWidget_5.addItem(dir_name)

    def add_skip_files(self):
        self._add_skip_paths(select_dirs=False)

    def add_skip_dirs(self):
        self._add_skip_paths(select_dirs=True)

    def _add_skip_paths(self, select_dirs):
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
        dialog_title = "选择要跳过的文件夹" if select_dirs else "选择要跳过的文件"
        dialog = QFileDialog(self, dialog_title, defalut_path)
        if select_dirs:
            dialog.setFileMode(QFileDialog.Directory)
            dialog.setOption(QFileDialog.ShowDirsOnly, True)
        else:
            dialog.setFileMode(QFileDialog.ExistingFiles)
            dialog.setOption(QFileDialog.ShowDirsOnly, False)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        for view in dialog.findChildren((QListView, QTreeView)):
            view.setSelectionMode(QAbstractItemView.MultiSelection)
        if dialog.exec_():
            file_paths = dialog.selectedFiles()
            if not file_paths:
                return
            skip_dirs = config_manager.project_dict[pj_name].get('skip_dirs', [])
            outside_paths = []
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    continue
                if select_dirs and not os.path.isdir(file_path):
                    continue
                rel_path = os.path.relpath(file_path, defalut_path)
                if rel_path == ".":
                    continue
                if rel_path.startswith(".."):
                    outside_paths.append(file_path)
                    continue
                rel_path = rel_path.replace("\\", "/")
                print('选择的文件夹路径为：', rel_path)
                if rel_path not in skip_dirs:
                    skip_dirs.append(rel_path)
            if skip_dirs:
                config_manager.project_dict[pj_name]['skip_dirs'] = skip_dirs
                config_manager.project_dict[pj_name]['skip_dirs_auto'] = False
                config_manager.update_project()
                self.show_skip_dirs()
                print('跳过的文件夹：', skip_dirs)
            if outside_paths:
                QMessageBox.warning(
                    self,
                    "提示",
                    "已忽略不在打包目录下的路径，请在当前打包目录中选择文件/文件夹。",
                    QMessageBox.Yes
                )

    def delete_skip_dirs(self):
        pj_name = self.label_5.text()
        skip_dirs = config_manager.project_dict[pj_name].get('skip_dirs', [])
        selected_item = self.listWidget_5.currentItem().text()
        if selected_item in skip_dirs:
            skip_dirs.remove(selected_item)
            config_manager.project_dict[pj_name]['skip_dirs'] = skip_dirs
            config_manager.project_dict[pj_name]['skip_dirs_auto'] = False
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
        print("部分编译启动")
        encrypt_manager.part_encrypt_file()
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

    def update_full_encrypt_text(self, text, status):
        color_map = {
            "error": QColor(200, 0, 0),
            "info": QColor(0, 160, 0),
            "warning": QColor(255, 165, 0)
        }
        color = color_map.get(status, QColor(0, 0, 0))
        format = QTextCharFormat()
        format.setForeground(color)
        if status == "info":
            format.setFontPointSize(10)
        else:
            format.setFontPointSize(12)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text+'\n', format)
