# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/24
@Author  : Liangjh
@File    : unZipManager.py
@Description:
"""
import os
import tarfile


class unZipManager:
    def __init__(self):
        self.local_zip_path = ''
        self.dest_path = ''

    def update_zip_path(self, local_zip_path):
        self.local_zip_path = local_zip_path

    def update_dest_path(self, dest_path):
        self.dest_path = dest_path

    def un_zip(self):
        import zipfile
        with zipfile.ZipFile(self.local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.dest_path)

    def unpack_conda_env(self, tar_gz_path, dest_path):
        """使用 tarfile 解压 conda 环境的 .tar.gz 文件"""
        print(f"开始解压 conda 环境：{tar_gz_path}")
        print(f"目标路径：{dest_path}")
        
        # 创建目标目录
        os.makedirs(dest_path, exist_ok=True)
        
        # 解压 tar.gz 文件
        with tarfile.open(tar_gz_path, 'r:gz') as tar:
            tar.extractall(dest_path)
        
        print(f"conda 环境解压完成：{dest_path}")
un_zip_manager = unZipManager()