import os
import zipfile

from Src.manager.SignalManager import signal_manager


class ZipManager:
    def __init__(self):
        self.target_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + r"\PyZip"
        self.target_zip_name = ''
        self.folder_to_zip = ['DLLs', 'include', 'Lib', 'Scripts', 'tcl','Library']
        self.files_to_zip = ['python.exe', 'python3.dll']
        self.src_path = ''

    def zip_folders_and_files(self):
        zip_name = os.path.join(self.target_path, self.target_zip_name)
        folders = []
        for i in self.folder_to_zip:
            abs_path = os.path.join(self.src_path, i)
            if os.path.exists(abs_path):
                folders.append(abs_path)
        print(f"待压缩的文件夹：{folders}")

        files = []
        for i in self.files_to_zip:
            abs_path = os.path.join(self.src_path, i)
            if os.path.exists(abs_path):
                files.append(abs_path)
        print(f"待压缩的文件：{files}")
        signal_manager.updateProgressBarValueSignal.emit(1)
        print("压缩文件到指定位置：", zip_name)
        task_count = len(folders) + len(files)
        print("需要压缩的数量：", task_count)
        current_count = 0
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            # 压缩多个文件夹
            for folder in folders:
                print(f"正在压缩文件夹：{folder}")
                for root, dirs, file_names in os.walk(folder):
                    print("遍历文件：",root, dirs, file_names)
                    for file_name in file_names:
                        file_path = os.path.join(root, file_name)
                        print(f"正在压缩文件：{file_path}")
                        # 将文件添加到zip中，保留文件路径
                        zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(folder)))
                current_count += 1
                # 打印百分比
                percent = round(current_count / task_count * 100, 2)
                signal_manager.updateProgressBarValueSignal.emit(int(percent))
                print("已完成：", percent, "%")
            # 压缩指定的多个文件
            for file in files:
                zipf.write(file, os.path.basename(file))
                current_count += 1
                # 打印百分比
                percent = round(current_count / task_count * 100, 2)
                signal_manager.updateProgressBarValueSignal.emit(int(percent))
                print("已完成：", percent, "%")

        print("压缩完成！")
        # 打开压缩路径
        os.startfile(os.path.dirname(zip_name))


zip_manager = ZipManager()

if __name__ == '__main__':
    # 使用示例
    zip_manager = ZipManager()
    zip_manager.folder_to_zip = [r'D:\Project\tools\packet_tool\Src\manager']  # 替换为你的文件夹名列表
    zip_manager.files_to_zip = [r'D:\Project\tools\packet_tool\Src\mainWindow.py',
                                r'D:\Project\tools\packet_tool\Src\mainWindow.ui']  # 替换为你的文件名列表
    zip_manager.target_zip_name = 'archive.zip'  # 输出的zip文件名

    zip_manager.zip_folders_and_files()
