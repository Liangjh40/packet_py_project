# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/6
@Author  : Liangjh
@File    : encryptManager.py
@Description:
"""
import glob
import os
import shutil
import subprocess
from pathlib import Path
from typing import Union, Optional

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from Src.manager.SignalManager import signal_manager
from Src.manager.configManager import config_manager


class EncryptManager:
    def __init__(self):
        self.env_name = None
        self.main_path = None
        self.dirs = []
        self.skip_dirs = []
        self.pj_name = None
        self.dst_path = None
        self.env_python_path = None
        self.part_files = []
        self.progress_prefix = "PROGRESS:"
        self.output_channel = "part"

    def update_main_path(self, pj_name):
        self.pj_name = pj_name
        main_file = config_manager.project_dict[pj_name]["path"]
        self.main_path = os.path.dirname(main_file)
        # self.main_path = 'D:\\'
        self.dst_path = os.path.join(self.main_path, "dist", self.pj_name)
        self.dirs = config_manager.project_dict[pj_name].get('copy_dirs', [])
        self.skip_dirs = config_manager.project_dict[pj_name].get('skip_dirs', [])
        print(f"更新需复制的文件夹:{pj_name}->{self.dirs}")

    def update_env_path(self, env_name):
        env_path = None
        env_info = config_manager.env_dict.get(env_name, {})
        if "local_env_path" in env_info:
            env_path = env_info["local_env_path"]
        if not env_path:
            # Fallback: resolve conda env path by name
            try:
                conda_env_name = env_name.replace(".tar.gz", "")
                result = subprocess.run(
                    ["conda", "env", "list"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if parts and parts[0] == conda_env_name:
                            for part in parts[1:]:
                                if os.path.isdir(part):
                                    env_path = part
                                    break
                            break
            except Exception:
                env_path = None
        if not env_path:
            signal_manager.messageBoxSignal.emit("未找到环境路径，请先确认环境已安装或重新添加环境")
            return
        # self.env_python_path = os.path.join(env_path, "python.exe")
        self.env_python_path = env_path
        self.env_name = env_name.split(".")[0]

    def set_env_path_by_venv(self, venv_path):
        self.env_python_path = venv_path
        self.env_name = None  # Flag to use direct python execution instead of conda

    def copy_dir(self):
        for dir_name in self.dirs:
            src_dir = os.path.join(self.main_path, dir_name)
            dst_dir = os.path.join(self.dst_path, dir_name)
            if os.path.isdir(src_dir):
                shutil.copytree(src_dir, dst_dir)
                print(f"文件夹{dir_name}复制完成")

    def delete_ui_file(self):
        # gui文件夹 删除ui文件
        gui_path = os.path.join(self.dst_path, "Gui")
        if not os.path.exists(gui_path):
            return
        for file_name in os.listdir(gui_path):
            if file_name.endswith(".ui"):
                os.remove(os.path.join(gui_path, file_name))

    def encrypt_file(self):
        import threading
        if not self.env_python_path and not self.env_name:
            signal_manager.messageBoxSignal.emit("未设置有效环境路径，请先选择环境")
            return
        self.output_channel = "full"
        # 全量编译入口
        self.task = threading.Thread(target=self.encrypt_file_thread)
        self.task.daemon = True
        self.task.start()

    def part_encrypt_file(self):
        self.output_channel = "part"
        signal_manager.updateProgressBarValueSignal.emit(0)
        try:
            self._part_encrypt_file_impl()
        except Exception as e:
            msg = f"编译异常退出：{e}"
            print(msg)
            self._emit_text(msg, "error")

    def _part_encrypt_file_impl(self):
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # packet_path = os.path.join(app_path, "dist", self.pj_name)
        print(f'打包好的软件目录：{self.dst_path}')
        self._emit_text(f'打包好的软件目录：{self.dst_path}', "info")
        # 执行前验证 py2pyd_global.py 是否在 app_path 目录中
        py_script = os.path.join(app_path, "py2pyd_global.py")
        if not os.path.exists(py_script):
            print(f"错误：py2pyd_global.py 不在 {app_path} 目录中！")
            self._emit_text(
                f"错误：py2pyd_global.py 不在 {app_path} 目录中！", "error"
            )
            return  # 终止执行，避免后续错误
        mid_dir = os.path.join(app_path, "midDir")  # 加密中间文件存放目录

        if not os.path.exists(mid_dir):
            os.makedirs(mid_dir)
        # 如果文件夹有文件，则删除
        clear_directory(mid_dir)

        if not self.part_files:
            msg = "未找到可加密文件，请先刷新修改文件列表或确认工程路径"
            print(msg)
            self._emit_text(msg, "error")
            return

        self._emit_text("开始加密文件", 'warning')
        copied_count = 0
        for src_file in self.part_files:
            try:
                # 构造目标文件的完整路径（目标根目录 + 源文件的相对路径）
                target_file = os.path.join(mid_dir, src_file)

                # 提取目标文件所在的目录路径（自动包含所有父目录）
                target_dir = os.path.dirname(target_file)

                # 递归创建目录（如果不存在），exist_ok=True 避免目录已存在时报错
                os.makedirs(target_dir, exist_ok=True)
                # print(f"已确保目录存在：{target_dir}")

                # 复制文件
                file_path = Path(self.main_path) / src_file
                shutil.copyfile(file_path, target_file)
                # print(f"已复制文件：{file_path} -> {target_file}")
                copied_count += 1

            except Exception as e:
                print(f"复制文件失败 {src_file}：{str(e)}")
        if copied_count == 0:
            msg = "复制文件到中转目录失败，未生成可加密文件"
            print(msg)
            self._emit_text(msg, "error")
            return

        # 加密文件
        bat_save_path = os.path.join(app_path, "run_py_script.bat")
        bat_save_path = Path(bat_save_path).resolve()  # 转换为绝对路径
        generate_conda_batch(self.env_python_path, py_script, mid_dir, bat_save_path)
        if not bat_save_path.exists():
            print(f"❌ 批处理文件生成失败：{bat_save_path}")
            self._emit_text(
                f"❌ 批处理文件生成失败：{bat_save_path}", "error"
            )
            return  # 终止执行，避免后续错误
        self._emit_text(
            f"✅ 批处理文件已生成：{bat_save_path}", "info"
        )
        cmd = f"{bat_save_path}"
        python_path = os.path.join(self.env_python_path, "python.exe")
        process = subprocess.Popen(cmd, shell=True, cwd=app_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # 捕获并打印输出内容
        while True:
            output = process.stdout.readline()
            if output:
                try:
                    # 优先尝试GBK（中文常见编码）
                    line = output.decode("gbk").strip()
                    print("运行output信息:", line)
                except UnicodeDecodeError:
                    # 若仍失败，忽略无法解码的字符
                    line = output.decode("utf-8", errors="ignore").strip()
                    print("运行output信息:", line)
                self._handle_progress_line(line)

            if output == b'' and process.poll() is not None:
                break

        # 检查mid_dir里文件数量是否与self.part_files 一致
        mid_files_count = count_files_recursive(mid_dir)
        if mid_files_count == len(self.part_files):
            msg = '加密完成，覆盖到打包好的软件目录'
            self._emit_text(msg, 'warning')
        else:
            msg = f'加密失败，加密文件数量：{mid_files_count}与源文件数量：{len(self.part_files)}不一致'
            self._emit_text(msg, 'error')
            return

        replace_same_files(mid_dir, self.dst_path)
        msg = f'任务完成！'
        self._emit_text(msg, 'warning')
        signal_manager.updateProgressBarValueSignal.emit(100)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.dst_path))))




    def encrypt_file_thread(self):
        signal_manager.updateProgressBarValueSignal.emit(0)
        try:
            self._encrypt_file_thread_impl()
        except Exception as e:
            msg = f"编译异常退出：{e}"
            print(msg)
            self._emit_text(msg, "error")

    def _encrypt_file_thread_impl(self):
        # 加密文件
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        skip_dirs_run = list(self.skip_dirs or [])
        if "Src" in skip_dirs_run:
            print("检测到跳过项包含 Src，已忽略该项以执行全量编译")
            skip_dirs_run = [d for d in skip_dirs_run if d != "Src"]
        for dir_name in self.dirs:
            dst_dir = os.path.join(self.dst_path, dir_name)  # Gui\ Src \ UpdaterSet...
            if dir_name == "Gui" or dir_name == "UpdaterSet":
                sub_dir = []
            else:
                # 打印路径dst_dir下的子文件夹
                sub_dir = list_subfolders(dst_dir)
                print(f"{dir_name}文件夹下的子文件夹{sub_dir}")
            if sub_dir:  # 存在子文件夹 单独编译子文件夹所有文件
                for sub_dir_name in sub_dir:
                    rel_path = os.path.join(dir_name, sub_dir_name)
                    if self._should_skip_path(rel_path, skip_dirs_run):
                        continue
                    sub_dst_dir = os.path.join(dst_dir, sub_dir_name)
                    print(f"加密{sub_dst_dir}文件夹")
                    python_exe = None
                    if self.env_python_path:
                        python_exe = os.path.join(self.env_python_path, "python.exe")
                        if not os.path.exists(python_exe):
                            python_exe = os.path.join(self.env_python_path, "Scripts", "python.exe")
                    if python_exe and os.path.exists(python_exe):
                        cmd_args = [
                            python_exe, "py2pyd_global.py", "all", "del", str(Path(sub_dst_dir)), python_exe
                        ]
                    else:
                        cmd_args = [
                            "conda", "run", "-n", self.env_name,
                            "python", "py2pyd_global.py", "all", "del", str(Path(sub_dst_dir)), "python"
                        ]

                    print(f"加密命令：{subprocess.list2cmdline(cmd_args)}")
                    process = subprocess.Popen(cmd_args, shell=False, cwd=app_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    # 捕获并打印输出内容
                    while True:
                        output = process.stdout.readline()
                        # error = process.stderr.readline()
                        if output:
                            try:
                                line = output.decode("utf-8").strip()
                            except UnicodeDecodeError:
                                line = output.decode("gbk", errors="ignore").strip()
                            print("运行output信息:", line)
                            self._handle_progress_line(line)
                        # if error:
                        #     print("运行error信息",error.decode("utf-8").strip(), file=sys.stderr)
                        if output == b'' and process.poll() is not None:
                            # print("nuitka打包完成")
                            break
                    if process.returncode not in (0, None):
                        msg = f"编译命令失败，返回码: {process.returncode}"
                        print(msg)
                        self._emit_text(msg, "error")
            else:  # 不存在子文件夹 直接编译整个文件夹
                if self._should_skip_path(dir_name, skip_dirs_run):
                    continue
                python_exe = None
                if self.env_python_path:
                    python_exe = os.path.join(self.env_python_path, "python.exe")
                    if not os.path.exists(python_exe):
                        python_exe = os.path.join(self.env_python_path, "Scripts", "python.exe")
                if python_exe and os.path.exists(python_exe):
                    cmd_args = [
                        python_exe, "py2pyd_global.py", "all", "del", str(Path(dst_dir)), python_exe
                    ]
                else:
                    cmd_args = [
                        "conda", "run", "-n", self.env_name,
                        "python", "py2pyd_global.py", "all", "del", str(Path(dst_dir)), "python"
                    ]
                print(f"加密命令：{subprocess.list2cmdline(cmd_args)}")
                process = subprocess.Popen(cmd_args, shell=False, cwd=app_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                # 捕获并打印输出内容
                while True:
                    output = process.stdout.readline()
                    # error = process.stderr.readline()
                    if output:
                        try:
                            line = output.decode("utf-8").strip()
                        except UnicodeDecodeError:
                            line = output.decode("gbk", errors="ignore").strip()
                        print("运行output信息:", line)
                        self._handle_progress_line(line)
                    # if error:
                    #     print("运行error信息",error.decode("utf-8").strip(), file=sys.stderr)
                    if output == b'' and process.poll() is not None:
                        # print("nuitka打包完成")
                        break
                if process.returncode not in (0, None):
                    msg = f"编译命令失败，返回码: {process.returncode}"
                    print(msg)
                    self._emit_text(msg, "error")
        print(f"加密完成")
        signal_manager.updateProgressBarValueSignal.emit(100)

    def _handle_progress_line(self, line):
        if not line:
            return
        if line.startswith("COUNT:"):
            try:
                count_part = line.split("COUNT:", 1)[1].strip()
                current, total = count_part.split("/", 1)
                msg = f"编译进度：{int(current)}/{int(total)}"
                self._emit_text(msg, "info")
            except Exception:
                pass
            return
        if line.startswith("TOTAL_TIME:"):
            try:
                seconds = float(line.split("TOTAL_TIME:", 1)[1].strip())
                msg = f"编译完成，总耗时：{seconds:.2f} s"
                self._emit_text(msg, "warning")
            except Exception:
                pass
            return
        if line.startswith(self.progress_prefix):
            try:
                value = int(line.split(self.progress_prefix, 1)[1])
                signal_manager.updateProgressBarValueSignal.emit(value)
            except Exception:
                pass

    def _emit_text(self, text, status):
        if self.output_channel == "full":
            signal_manager.updateFullEncryptTextSignal.emit(text, status)
        else:
            signal_manager.updatePartEncryptTextSignal.emit(text, status)

    @staticmethod
    def _should_skip_path(rel_path, skip_dirs):
        if not skip_dirs:
            return False
        norm_path = rel_path.replace("\\", "/").strip("/")
        for entry in skip_dirs:
            entry_norm = str(entry).replace("\\", "/").strip("/")
            if not entry_norm:
                continue
            if "/" in entry_norm:
                if norm_path == entry_norm or norm_path.startswith(entry_norm + "/"):
                    return True
            else:
                if norm_path == entry_norm or norm_path.startswith(entry_norm + "/"):
                    return True
        return False


def list_subfolders(folder_path):
    """
    列出指定文件夹下的所有子文件夹名称
    :param folder_path: 要检查的文件夹路径
    :return: 子文件夹名称列表
    """
    if not os.path.exists(folder_path):
        print(f"错误：路径 {folder_path} 不存在")
        return []
    if not os.path.isdir(folder_path):
        print(f"错误：{folder_path} 不是一个文件夹")
        return []

    subfolders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subfolders.append(item)
    return subfolders


def generate_conda_batch(
        conda_env_path: Union[str, Path],
        py_script_path: Union[str, Path],
        mid_dir: Union[str, Path],
        bat_save_path: Union[str, Path] = "run_py_script.bat"
) -> None:
    """
    生成用于激活conda环境并执行Python脚本的批处理文件

    参数:
        conda_env_path: conda虚拟环境的绝对路径（如 D:/conda/envs/explorer38）
        py_script_path: 要执行的Python脚本的绝对路径
        mid_dir: 中转文件夹的绝对路径（作为脚本参数传入）
        bat_save_path: 生成的.bat文件保存路径（默认当前目录下的 run_py_script.bat）
    """
    # 转换为Path对象，自动处理路径格式和跨平台兼容
    conda_env = Path(conda_env_path).resolve()
    py_script = Path(py_script_path).resolve()
    mid = Path(mid_dir).resolve()
    bat_path = Path(bat_save_path).resolve()

    # 从虚拟环境路径提取conda根目录（默认虚拟环境在 conda根目录/envs/ 下）
    # 例如：conda_env = D:/conda/envs/explorer38 → conda_root = D:/conda
    conda_root = conda_env.parent.parent  # parent是envs目录，再上一级是conda根目录

    # 定位conda激活脚本（activate.bat）的路径
    activate_bat = conda_root / "Scripts" / "activate.bat"
    if not activate_bat.exists():
        raise FileNotFoundError(f"未找到conda激活脚本：{activate_bat}\n请检查conda虚拟环境路径是否正确")

    python_exe = conda_env / "python.exe"
    if not python_exe.exists():
        raise FileNotFoundError(f"未找到python.exe：{python_exe}\n请检查conda虚拟环境路径是否正确")

    # 构建批处理文件内容
    # 1. @echo off：关闭命令回显（避免输出冗余命令）
    # 2. call激活脚本：激活指定虚拟环境
    # 3. 执行Python脚本：传入参数 all del [mid_dir]
    bat_content = f'''@echo off
:: 激活conda虚拟环境
call "{activate_bat}" "{conda_env}"

:: 显示当前Python环境信息（用于排查Cython环境问题）
"{python_exe}" -c "import sys;print('PYTHON_EXE:'+sys.executable)"
"{python_exe}" -c "import Cython,sys;print('CYTHON_VER:'+Cython.__version__)"

:: 执行Python脚本（传入参数：all del [中转文件夹]）
"{python_exe}" "{py_script}" all del "{mid}" "{python_exe}"


:: 可选：执行完成后暂停（方便查看输出，按需启用）
:: pause
'''

    # 写入批处理文件（用utf-8编码，避免中文乱码）
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    print(f"✅ 批处理文件已生成：\n保存路径：{bat_path}")

def run_batch_file(
        bat_path: Union[str, Path],
        timeout: Optional[int] = 300,  # 超时时间（秒），None 表示不限制
        cwd: Optional[Union[str, Path]] = None  # 执行目录，None 表示当前工作目录
) -> bool:
    """
    执行批处理文件并返回执行结果

    参数:
        bat_path: 批处理文件（.bat）的绝对路径
        timeout: 超时时间（秒），超过此时长自动终止进程，默认 300 秒
        cwd: 执行批处理的工作目录，默认使用当前目录

    返回:
        执行成功返回 True，失败/超时返回 False
    """
    # 强制转换为绝对路径并校验
    bat_file = Path(bat_path).resolve()  # 无论传入相对/绝对路径，都转为绝对路径
    print(f"📌 尝试执行的批处理文件（绝对路径）：{bat_file}")  # 关键：打印实际路径

    if not bat_file.exists():
        print(f"❌ 批处理文件不存在（绝对路径）：{bat_file}")
        return False
    if bat_file.suffix.lower() != ".bat":
        print(f"❌ 不是批处理文件：{bat_file}")
        return False

    # 确定执行目录（cwd）
    working_dir = Path(cwd).resolve() if cwd else Path(os.getcwd()).resolve()
    if not working_dir.exists():
        print(f"❌ 工作目录不存在：{working_dir}")
        return False

    # try:
    if True:
        print(f"📌 开始执行批处理文件：{bat_file}")
        print(f"📌 工作目录：{working_dir}")
        print(f"📌 超时设置：{timeout} 秒（0 表示不限制）\n")

        # 执行批处理文件
        # shell=True 确保在 Windows 中正确调用 cmd.exe 执行 .bat
        # executable="cmd.exe" 显式指定用 cmd 执行，避免兼容性问题
        process = subprocess.Popen(
            str(bat_file),  # 批处理文件路径（转换为字符串）
            shell=True,
            executable="C:\Windows\system32\cmd.exe",  # 强制使用 cmd.exe 执行批处理
            cwd=str(working_dir),  # 工作目录
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE,  # 捕获标准错误
            # text=True,  # 输出为字符串（而非 bytes）
            # encoding="gbk"  # 匹配 Windows 命令行编码，避免中文乱码
        )

        # 实时打印输出日志（同时捕获 stdout 和 stderr）
        print("=== 批处理执行日志 ===")
        while True:
            # 读取字节流（stdout）
            stdout_bytes = process.stdout.readline()
            if stdout_bytes:
                # 尝试用 gbk 解码，无法解码的字符忽略（replace 替换为�）
                try:
                    stdout_line = stdout_bytes.decode("gbk")
                except UnicodeDecodeError:
                    # 若 gbk 失败，尝试 utf-8（兼容部分特殊字符）
                    try:
                        stdout_line = stdout_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        # 仍失败则忽略错误字符
                        stdout_line = stdout_bytes.decode("gbk", errors="ignore")
                print(f"[输出] {stdout_line.strip()}")

            # 读取字节流（stderr）
            stderr_bytes = process.stderr.readline()
            if stderr_bytes:
                # 同上，灵活解码错误输出
                try:
                    stderr_line = stderr_bytes.decode("gbk")
                except UnicodeDecodeError:
                    try:
                        stderr_line = stderr_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        stderr_line = stderr_bytes.decode("gbk", errors="ignore")
                print(f"[错误] {stderr_line.strip()}")

            if not stdout_bytes and not stderr_bytes and process.poll() is not None:
                break

        try:
            return_code = process.wait(timeout=timeout) if timeout is not None else process.wait()
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"\n❌ 执行超时（{timeout}秒）")
            return False

        if return_code == 0:
            print(f"\n✅ 执行成功（返回码：{return_code}）")
            return True
        else:
            print(f"\n❌ 执行失败（返回码：{return_code}）")
            return False



    # except Exception as e:
    #     print(f"\n❌ 执行过程发生错误：{str(e)}")
    #     return False


def clear_directory(mid_dir):
    """
    清空指定目录下的所有文件和子文件夹（保留当前目录本身）
    :param mid_dir: 要清空的目录路径
    """
    # 检查目录是否存在
    if not os.path.exists(mid_dir):
        print(f"目录不存在：{mid_dir}")
        return
    if not os.path.isdir(mid_dir):
        print(f"不是目录：{mid_dir}")
        return

    # 遍历目录下的所有条目
    for item in os.listdir(mid_dir):
        item_path = os.path.join(mid_dir, item)

        try:
            # 如果是文件，直接删除
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                print(f"已删除文件：{item_path}")
            # 如果是文件夹，递归删除整个文件夹（包括内部所有内容）
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"已删除文件夹及内容：{item_path}")
        except Exception as e:
            print(f"删除失败 {item_path}：{str(e)}")


def count_files_recursive(mid_dir):
    """统计目录及其所有子文件夹中的文件总数（递归）"""
    if not os.path.exists(mid_dir) or not os.path.isdir(mid_dir):
        print(f"目录不存在或不是有效目录：{mid_dir}")
        return 0

    file_count = 0
    # 递归遍历所有子目录
    for root, dirs, files in os.walk(mid_dir):
        file_count += len(files)  # 累加当前目录的文件数
    return file_count

def get_filename_without_ext(file_path):
    """
    从文件路径中提取不带后缀的文件名
    :param file_path: 文件的完整路径（如 "Src/DialogMangement/GaitComponent/VideoPreview.py"）
    :return: 不带后缀的文件名（如 "VideoPreview"）
    """
    # 1. 从完整路径中提取带后缀的文件名（如 "VideoPreview.py"）
    filename_with_ext = os.path.basename(file_path)
    # 2. 分割文件名和后缀（splitext返回元组：(文件名, 后缀)）
    filename_without_ext = os.path.splitext(filename_with_ext)[0]
    return filename_without_ext


def replace_same_files(src_root, dst_root):
    """
    仅替换目标文件夹中与源文件夹同名的子文件夹内的同名文件
    不创建新的顶层文件夹（仅处理源和目标都存在的顶层子文件夹）
    :param src_root: 源根目录（如 midDir）
    :param dst_root: 目标根目录
    """
    # 获取源根目录下的所有顶层子文件夹（仅文件夹，不包括文件）
    src_dirs = [
        d for d in os.listdir(src_root)
        if os.path.isdir(os.path.join(src_root, d))
    ]

    for dir_name in src_dirs:
        # 源子文件夹完整路径（如 midDir/Gui）
        src_subdir = os.path.join(src_root, dir_name)
        # 目标子文件夹完整路径（如 target/Gui）
        dst_subdir = os.path.join(dst_root, dir_name)

        # 仅处理目标中已存在的同名子文件夹
        if not os.path.exists(dst_subdir) or not os.path.isdir(dst_subdir):
            print(f"目标中不存在同名文件夹 {dir_name}，跳过处理")
            continue

        print(f"开始处理文件夹：{dir_name}（替换同名文件）")

        # 递归遍历源子文件夹中的所有文件
        for src_file in [
            os.path.join(root, file)
            for root, _, files in os.walk(src_subdir)
            for file in files
        ]:
            # 计算文件相对于源子文件夹的相对路径（用于匹配目标路径）
            rel_path = os.path.relpath(src_file, src_subdir)
            # 目标文件完整路径
            dst_file = os.path.join(dst_subdir, rel_path)

            # 确保目标文件的父目录存在（如果源有嵌套子文件夹，目标也会创建对应结构）
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

            # 复制并覆盖同名文件（copy2 保留文件元数据）
            shutil.copy2(src_file, dst_file)
            print(f"已替换文件：{dst_file}")


encrypt_manager = EncryptManager()
