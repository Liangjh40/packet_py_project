import glob
import os
import shutil
import subprocess
import sys
import time
import zipfile
# from multiprocessing import Queue

# from tqdm import tqdm
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


def activate_environment():
    # 指定要激活的conda环境名称
    conda_env_name = "py38"

    # 使用subprocess执行激活conda环境的命令
    process = subprocess.Popen(["conda", "activate", conda_env_name], shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    # 获取输出和错误信息（可选）
    output, error = process.communicate()
    # 检查命令是否执行成功
    if process.returncode == 0:
        print("conda环境激活成功")
        return True
    else:
        print("conda环境激活失败")
        print("错误信息:", error.decode("utf-8"))
        return False


def packing_project(cmd,main_file, path):       # cmd1 测试  cmd2 正式
    # 定义要执行的命令
    # nuitka_executable = r"D:\conda\envs\gait\Scripts\nuitka.bat"  # nuitka实际路径  py39
    nuitka_executable = r"D:\conda\envs\explorer38\Scripts\nuitka.bat"  # nuitka实际路径  py38
    # 测试，有控制台
    # command1 = f"{nuitka_executable} --standalone --mingw64 --show-memory  --nofollow-imports --enable-plugin=pyqt5 --follow-import-to=Gui,Src  --output-dir=dist {os.path.join(path, main_file)}"
    command1 = f"{nuitka_executable} --standalone --mingw64 --show-memory  --follow-import-to=Gui,Src  --output-dir=dist {os.path.join(path, main_file)}"
    # 正式版，无控制台，有图标
    # ico = os.path.join(path, "Gui", "resource", "asd.ico")
    ico = r"D:\GiteeProject\BehaviorAtlasExplorer-feature\Gui\resource\Explorer_mouse.ico"
    # command2 = f"{nuitka_executable} --standalone --windows-icon-from-ico={ico} --windows-disable-console --mingw64 --nofollow-imports --show-memory --show-progress --enable-plugin=pyqt5 --follow-import-to==Gui,Src  --output-dir=dist {os.path.join(path, main_file)}"
    command2 = f"{nuitka_executable} --standalone --windows-icon-from-ico={ico} --windows-disable-console --mingw64  --show-memory --show-progress --follow-import-to==Gui,Src  --output-dir=dist {os.path.join(path, main_file)}"
    # 执行命令
    print("执行命令:", command1 if cmd==1 else command2)
    # process = subprocess.Popen(command2, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = subprocess.Popen(command1 if cmd==1 else command2, cwd=path, stdout=subprocess.PIPE)


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
    filename = main_file.split(".")[0]
    if os.path.exists(os.path.join(path, "dist", filename + ".dist")):
        print("nuitka打包完成")
        return True
    else:
        print("nuitka打包失败")
        return False


def unzip_file(source_zip, target_dir):
    """ 指定源压缩包和目标解压路径
    source_zip = 'your_archive.zip'
    target_dir = '/path/to/extract/to/'
    """

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        # 获取压缩包中的所有文件
        files = zip_ref.namelist()
        total_files = len(files)
        # print(f"开始解压 {total_files} 个文件到 {target_dir}")

        # 解压所有文件到指定目录，并显示进度
        for file in tqdm(files, position=0):
            target_file = target_dir + file
            # 创建必要的中间目录（如果需要）
            parent_dir = os.path.dirname(target_file)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            zip_ref.extract(file, target_dir)
        print(f"解压完成")


def py2pyd(abs_path, del_py=True):
    file_dir = os.path.split(abs_path)[0]  # 编译文件路径 D:\Pack\py2pyd\Gui
    print("编译文件路径", file_dir)
    filename = os.path.split(abs_path)[1]  # 不带路径的文件名 编译文件名 AddModelDialogBase.py
    print("编译文件名", filename)
    cmd = f"cythonize -i {abs_path}"
    process = subprocess.Popen(cmd, cwd=file_dir,shell=True, stdout=subprocess.PIPE)

    while True:
        output = process.stdout.readline()
        # if output:
        #     print("运行output信息", output.decode("GBK"))
        if output == b'' and process.poll() is not None:
            break

    filename_no_extension = os.path.splitext(filename)[0]
    filename_no_extension_path = os.path.join(file_dir, filename_no_extension + ".c")
    os.remove(filename_no_extension_path)  # 删除临时文件 .c
    if del_py:
        os.remove(abs_path)
    print(f"{filename_no_extension + '.pyd'}编译完成")


def get_all_file(path):  # 遍历此目录下的所有py文件，包含子目录里的py
    for root, dirs, files in os.walk(path):
        print("get_all_file:root, dirs, files", root, dirs, files)
        for name in tqdm(files):
            if name.endswith(".py") and name != "__init__.py" and name != "start_app.py":
                file_path = os.path.join(root, name)
                print("DEBUG:搜索到的文件，传入函数", file_path)
                py2pyd(file_path)


def del_temp_dir(root_path, choice_dir):
    for dir in choice_dir:
        target_path = os.path.join(root_path, dir)
        print(f"DEBUG:target_path", target_path)
        for root, dirs, files in os.walk(target_path):
            for name in dirs:
                # print(f"DEBUG:name", name)
                if name == 'build':
                    dir_path = os.path.join(root, name)
                    try:
                        shutil.rmtree(dir_path)
                        print(f"成功删除文件夹及其所有内容: {dir_path}")
                    except FileNotFoundError:
                        print(f"指定的文件夹不存在: {dir_path}")
                    except PermissionError:
                        print(f"没有足够的权限删除文件夹: {dir_path}")
                    except Exception as e:
                        print(f"删除文件夹时发生错误: {e}")


def copy_dir(src, dir, dst):
    # for dir in tqdm(dirs):
    #     print(f"DEBUG:copy_dir", dir)
    src_dir = os.path.join(src, dir)
    dst_dir = os.path.join(dst, dir)
    if os.path.isdir(src_dir):
        shutil.copytree(src_dir, dst_dir)
        print(f"文件夹{dir}复制完成")


def move_dir(src, dir, dst):
    try:
        # for dir in tqdm(dirs):
        src_dir = os.path.join(src, dir)
        dst_dir = os.path.join(dst, dir)
        if os.path.isdir(src_dir):
            shutil.move(src_dir, dst_dir)
            print(f"文件夹{dir}移动完成")
    except Exception as e:
        print(f"移动文件夹时发生错误: {e}")


def process_dir(current_directory, mid_dir, target_dir, dir_name):
    # 这里将原本分散在循环内的操作整合进一个函数，接收需要的目录路径作为参数
    print(">>>>>>>>>>>>","当前操作的文件夹：", current_directory,"<<<<<<<<<<<<<")
    copy_dir(current_directory, dir_name, mid_dir)
    get_all_file(os.path.join(mid_dir, dir_name))
    move_dir(mid_dir, dir_name, target_dir)


def main_interface():
    # 修改当前工作目录
    new_directory = r"D:\GiteeProject\BehaviorAtlasExplorer-feature"
    os.chdir(new_directory)
    # 确认当前工作目录已经修改
    current_directory = os.getcwd()
    print("当前工作目录:", current_directory)
    main_file = "BehaviorAtlasExplorer.py"  # 打包的主文件
    # 指定源压缩包和目标解压路径
    source_zip = r'D:\Project\tools\auto_packaging\Save\env_gait.zip'
    target_dir = os.path.join(current_directory, "dist", "BehaviorAtlasExplorer.dist\\")
    dirs = ["Gui", "Src", "locales"]

    start = time.time()
    # 生成.exe文件
    res = packing_project(2, main_file, current_directory)
    if not res:
        print("打包失败")
        return
    print("生成.exe文件")
    # # 解压zip文件py38环境
    # thread = Thread(target=unzip_file, args=(source_zip, target_dir))
    # thread.daemon = False
    # thread.start()
    #
    # # # 逻辑代码复制到临时路径->如 D:\build    -> 编译完再复制到target_dir
    # mid_dir = r'D:\build'
    # queue = Queue()
    # for i in dirs:
    #     process_dir(current_directory, mid_dir, target_dir, i)
    #     queue.put(i)
    # with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    #     while not queue.empty():
    #         dir = queue.get()
    #         executor.submit(process_dir, current_directory, mid_dir, target_dir, dir)


    # executor.shutdown(wait=True)


    end = time.time()
    print("打包完成,耗时:", end - start, "s")
    print("打包路径:", target_dir)


main_interface()
