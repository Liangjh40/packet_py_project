# coding=utf-8
# python3
"""
@FileName：py2pyd.py
@Author: FangXiang
@Company: Shenzhen BayOne-Biotech Co., LTD.
@Email: fangxiang@bayonesz.com
@CreateFileTime: 2024/1/22 15:59
@Description: Python批量编译程序
    命令行参数说明:
    all:对目录及子目录下的所有py文件进行编译
    one:对单个py文件进行编译
    del:编译完删除py文件。此操作无法恢复、慎用！！！
    nodel:编译完不删除py文件
    例子：
    python py2pyd.py all del D:\PYTHON\toPYD\test
    python py2pyd.py one nodel D:\PYTHON\toPYD\test\mycode.py
"""


import os, shutil, time, sys, glob
try:
    from setuptools import setup	# 检测是否安装了cython
except:
    print("\n请先安装cython模块：pip install cython\n")
    sys.exit()

def add_cython_directive(file_path):
    """在单个.py文件第一行插入# cython: language_level=3"""
    # 检查文件是否为.py
    if not file_path.endswith(".py"):
        return False

    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 检查第一行是否已存在该声明
        if lines and lines[0].strip() == "# cython: language_level=3":
            print(f"已处理: {file_path} (无需修改)")
            return True

        # 在第一行插入声明
        with open(file_path, "w", encoding="utf-8") as f:
            # 插入新行
            f.write("# cython: language_level=3\n")
            # 写入原有内容
            f.writelines(lines)

        print(f"已更新: {file_path}")
        return True

    except Exception as e:
        print(f"处理失败 {file_path}: {str(e)}")
        return False
    
def py2pyd(path):
    print("当前处理的文件：", path)
    add_cython_directive(path)
    folder_path = os.path.dirname(path)  # 文件夹路径
    print("folder_path =", folder_path)
    file_path = os.path.split(path)[1]  # 不带路径的文件名
    print("file_path =", file_path)
    os.chdir(folder_path)
    with open('setup.py', 'w') as f:    # 自动生成单独的setup.py文件
        f.write('from setuptools import setup\n')
        f.write('from Cython.Build import cythonize\n')
        f.write('setup(\n')
        f.write("name='test',\n")
        f.write("ext_modules=cythonize('%s')\n" % file_path)
        f.write(")\n")
    if env:
        os.system(f'{env} setup.py build_ext --inplace')    #py编译开始
    else:
        os.system('python setup.py build_ext --inplace')    #py编译开始

    filename = file_path.split('.py')[0]    #文件名
    time.sleep(2)
    pyd_name = '%s\\%s.pyd' % (folder_path, filename)   #pyd文件名
    if os.path.exists(pyd_name): os.remove(pyd_name)    #删除老的pyd

    try:
        amd64_pyd = glob.glob(filename + "*.pyd")   #获取pyd文件的全名，类似***.cp38-win_amd64.pyd
        print("生成了PYD："+ amd64_pyd[0])
    except Exception as e:
        print("生成了PYD ")
    # os.rename('%s\\%s.%s-win_%s.pyd' % (folder_path, filename, cpxx, amdxx), pyd_name)
    # os.rename(amd64_pyd[0], pyd_name)  #改名字，删除多余的cp38-win_amd64.等
    os.remove('%s.c' % filename)    # 删除临时文件
    build_folder_path = os.path.join(folder_path, 'build')
    shutil.rmtree(build_folder_path)    # 删除掉生成的build文件夹
    os.remove('setup.py')   # 删除掉生成的setup.py
    if del_py == 'del':   # 删除py源文件，无法恢复，慎用！
        os.remove(file_path)


def get_all_file(path):  # 遍历此目录下的所有py文件，包含子目录里的py
    for root, dirs, files in os.walk(path):
        print("当前文件夹文件：", files)
        if "__init__.py" in files:
            os.rename(os.path.join(root, "__init__.py"), os.path.join(root, "__init__.pyTemp"))
            print("已将__init__.py文件改名为__init__.pyTemp")
        for name in files:
            if name.endswith(".py") and name != "__init__.py" and name != 'icons_rc.py':
                file_path = os.path.join(root, name)
                py2pyd(file_path)
    for root, dirs, files in os.walk(path):
        if "__init__.pyTemp" in files:
            os.rename(os.path.join(root, "__init__.pyTemp"), os.path.join(root, "__init__.py"))
            print("已将__init__.pyTemp文件改名为__init__.py")

if __name__ == "__main__":
    if len(sys.argv) <= 3:  # 判断命令行参数是否合法
        print("\n命令行参数错误...\n")
        sys.exit()

    one_all, del_py, paths, env = sys.argv[1:5]  # 获取命令行参数

    if one_all == 'one':
        py2pyd(paths)
    else:
        get_all_file(paths)
