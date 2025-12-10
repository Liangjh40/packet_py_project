# -*- coding: utf-8 -*-
"""
@Time    : 2025/3/24
@Author  : Liangjh
@File    : unZipManager.py
@Description:
"""

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
un_zip_manager = unZipManager()