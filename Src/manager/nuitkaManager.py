# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/6
@Author  : Liangjh
@File    : nuitkaManager.py
@Description:
"""
import os
import shutil
import subprocess

from Src.manager.configManager import config_manager


class NuitkaManager:
    def __init__(self):
        self.default_env_path = config_manager.env_dict["explorer38.zip"]["local_env_path"]
        self.nuitka_path = os.path.join(self.default_env_path, "Scripts", "nuitka.bat")  # 默认py38的nuitka路径
        self.main_file = None   # 绝对路径
        self.ico = None  # ico路径

    def update_project_path(self, pj_name):
        self.main_file = config_manager.project_dict[pj_name]["path"]
        self.ico = config_manager.project_dict[pj_name]["icon"]
        print(f"当前项目路径：{self.main_file}")
        print(f"当前项目ico路径：{self.ico}")

    def update_nuitka_path(self, env_name):
        self.default_env_path = config_manager.env_dict[env_name]["local_env_path"]
        self.nuitka_path = os.path.join(self.default_env_path, "Scripts", "nuitka.bat")
        print(f"当前环境nuitka路径：{self.nuitka_path}")



    def packing_project(self):
        command_cmd = f"{self.nuitka_path} --standalone --windows-icon-from-ico={self.ico}  --mingw64 --show-memory  --follow-import-to=Gui,Src  --output-dir=dist {self.main_file}"
        command_no_cmd = f"{self.nuitka_path} --standalone --windows-icon-from-ico={self.ico} --windows-disable-console --mingw64  --show-memory --show-progress --follow-import-to==Gui,Src  --output-dir=dist {self.main_file}"
        filename = os.path.basename(self.main_file).split(".")[0]
        target_dir = os.path.join(os.path.dirname(self.main_file), "dist", filename + ".dist")
        print(f'主文件路径：{self.main_file}')
        dist_path = os.path.join(os.path.dirname(self.main_file), "dist")
        if os.path.exists(dist_path):
            shutil.rmtree(dist_path)
        for command in [command_cmd, command_no_cmd]:
            print('执行命令：', command)
            process = subprocess.Popen(command,  cwd=os.path.dirname(self.main_file), stdout=subprocess.PIPE)
            # 捕获并打印输出内容
            while True:
                output = process.stdout.readline()
                # error = process.stderr.readline()
                if output:
                    print("运行output信息:", output.decode("utf-8").strip())
                # if error:
                #     print("运行error信息",error.decode("utf-8").strip(), file=sys.stderr)
                if output == b'' and process.poll() is not None:
                    # print("nuitka打包完成")
                    break
            # 检查打包是否完成

            if not os.path.exists(target_dir):
                print("nuitka打包失败")
                return False
            else:
                print("nuitka打包完成")
                if "windows-disable-console" not in command:
                    # 文件改名
                    os.rename(os.path.join(target_dir, filename + ".exe"),
                              os.path.join(target_dir, filename + '-cmd.exe'))
                    os.rename(target_dir, os.path.join(os.path.dirname(self.main_file), "dist", filename))
        # 移动文件到指定目录
        shutil.move(os.path.join(target_dir, filename + ".exe"), os.path.join(os.path.dirname(self.main_file), "dist", filename, filename + ".exe"))

        os.startfile(os.path.join(os.path.dirname(self.main_file), "dist", filename))

nuitka_manager = NuitkaManager()