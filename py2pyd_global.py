# coding=utf-8
# python3
"""
@FileName：py2pyd_global.py
@Author: FangXiang (ref), Codex
@Description: Global compile with merged cythonize + directory-level parallel use.
    命令行参数说明:
    all: 对目录及子目录下的所有py文件进行编译
    one: 对单个py文件进行编译
    del: 编译完删除py文件。此操作无法恢复、慎用！！！
    nodel: 编译完不删除py文件
    例子：
    python py2pyd_global.py all del D:\PYTHON\toPYD\test python skipA,skipB
    python py2pyd_global.py one nodel D:\PYTHON\toPYD\test\mycode.py python
"""

import json
import os
import shutil
import sys
import time
import glob
import re
import keyword
from pathlib import Path
import logging
import sysconfig

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"py2pyd_global_{time.strftime('%Y%m%d_%H%M%S')}.log")
VERBOSE = False
PROGRESS_PREFIX = "PROGRESS:"
COUNT_PREFIX = "COUNT:"
TIME_PREFIX = "TOTAL_TIME:"


def _safe_print(msg):
    try:
        print(msg)
    except Exception:
        try:
            data = str(msg).encode("utf-8", errors="replace")
            sys.stdout.buffer.write(data + b"\n")
            sys.stdout.buffer.flush()
        except Exception:
            pass


def log(msg, also_print=False):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    if also_print or VERBOSE:
        _safe_print(msg)

def emit_progress(value):
    try:
        percent = max(0, min(100, int(value)))
        print(f"{PROGRESS_PREFIX}{percent}")
    except Exception:
        pass

def emit_count(current, total):
    try:
        print(f"{COUNT_PREFIX}{int(current)}/{int(total)}")
    except Exception:
        pass

def emit_total_time(seconds):
    try:
        print(f"{TIME_PREFIX}{seconds:.2f}")
    except Exception:
        pass

os.environ.setdefault("CYTHON_DEFAULT_ENCODING", "utf-8")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

try:
    from setuptools import setup  # 检测是否安装了cython
    from Cython.Build import cythonize
    try:
        from Cython.Compiler import Options as cy_options
        cy_options.output_encoding = "utf-8"
    except Exception:
        pass
    try:
        from distutils import log as dist_log
        dist_log.set_threshold(dist_log.ERROR)
        dist_log.info = lambda *args, **kwargs: None
        logging.getLogger().setLevel(logging.ERROR)
        logging.disable(logging.WARNING)
    except Exception:
        pass
except Exception:
    log("请先安装cython模块：pip install cython", also_print=True)
    sys.exit()


def add_cython_directive(file_path):
    """在单个.py文件第一行插入# cython: language_level=3，并确保utf-8编码声明"""
    if not file_path.endswith(".py"):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        coding_re = re.compile(r"coding[:=]\s*([-\w.]+)")
        has_coding = any(coding_re.search(line) for line in lines[:2])
        has_cython = any(line.strip() == "# cython: language_level=3" for line in lines[:5])

        new_lines = []
        idx = 0
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            idx = 1

        if not has_coding:
            new_lines.append("# -*- coding: utf-8 -*-\n")

        if not has_cython:
            new_lines.append("# cython: language_level=3\n")

        new_lines.extend(lines[idx:])

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log(f"已更新: {file_path}")
        return True
    except Exception as e:
        log(f"处理失败 {file_path}: {str(e)}", also_print=True)
        return False


def record_failed_file(file_path):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    failed_file_txt = os.path.join(root_dir, 'failed_compile.txt')
    with open(failed_file_txt, 'a', encoding='utf-8') as f:
        f.write(file_path + '\n')


def load_skip_dirs_from_config(target_path):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    if not os.path.exists(config_path):
        return []

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        log(f"读取config.json失败: {e}", also_print=True)
        return []

    project_dict = config.get('project', {})
    p = Path(target_path).resolve()
    # path可能是 dist/{pj_name} 或 dist/{pj_name}/{dir}
    project_name = p.name
    if project_name not in project_dict:
        project_name = p.parent.name

    skip_dirs = project_dict.get(project_name, {}).get('skip_dirs', [])
    if skip_dirs:
        log(f"配置跳过的文件夹: {skip_dirs}")
    return skip_dirs


def load_compile_threads_from_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    if not os.path.exists(config_path):
        return None
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        settings = config.get("settings", {})
        threads = settings.get("compile_threads")
        if isinstance(threads, int) and threads > 0:
            return threads
    except Exception:
        return None
    return None


def is_valid_module_path(rel_path):
    module_path = os.path.splitext(rel_path)[0]
    parts = re.split(r"[\\/]+", module_path)
    for part in parts:
        if not part:
            return False
        if not part.isidentifier():
            return False
        if keyword.iskeyword(part):
            return False
    return True


def collect_py_files(root_path, skip_dirs):
    """遍历目录并收集py文件，保持与原逻辑相同的打印与__init__.py处理"""
    files_rel = []
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if not is_skipped_path(root_path, os.path.join(root, d), skip_dirs)]
        log(f"当前文件夹文件：{files}")
        ensure_init_for_package_dirs(root, files)
        for name in files:
            if name.endswith(".py") and name != "__init__.py" and name != 'icons_rc.py':
                file_path = os.path.join(root, name)
                rel_path = os.path.relpath(file_path, root_path)
                if is_skipped_path(root_path, file_path, skip_dirs):
                    log(f"跳过已配置文件: {rel_path}")
                    continue
                if not is_valid_module_path(rel_path):
                    log(f"跳过无效模块名文件: {rel_path}", also_print=True)
                    record_failed_file(os.path.join(root_path, rel_path))
                    continue
                files_rel.append(rel_path)
    return files_rel


def restore_init_files(root_path, skip_dirs):
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if not is_skipped_path(root_path, os.path.join(root, d), skip_dirs)]
        if "__init__.pyTemp" in files:
            os.rename(os.path.join(root, "__init__.pyTemp"), os.path.join(root, "__init__.py"))
            log("已将__init__.pyTemp文件改名为__init__.py")


def ensure_init_for_package_dirs(root, files):
    if "__init__.py" in files:
        return
    has_py = any(name.endswith(".py") and name not in ("__init__.py", "icons_rc.py") for name in files)
    if not has_py:
        return
    try:
        init_path = os.path.join(root, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("# -*- coding: utf-8 -*-\n")
            log(f"已创建: {init_path}")
    except Exception:
        pass


def is_skipped_path(root_path, path, skip_dirs):
    if not skip_dirs:
        return False
    rel_path = os.path.relpath(path, root_path).replace("\\", "/").strip("/")
    for entry in skip_dirs:
        entry_norm = str(entry).replace("\\", "/").strip("/")
        if not entry_norm:
            continue
        if "/" in entry_norm:
            if rel_path == entry_norm or rel_path.startswith(entry_norm + "/"):
                return True
        else:
            if rel_path == entry_norm or rel_path.startswith(entry_norm + "/"):
                return True
    return False


def cleanup_build_files(root_path, files_rel, del_py, delete_py=True):
    for rel_path in files_rel:
        abs_path = os.path.join(root_path, rel_path)
        base_name = os.path.splitext(abs_path)[0]
        c_path = base_name + '.c'
        if os.path.exists(c_path):
            try:
                os.remove(c_path)
            except Exception:
                pass
        if del_py == 'del' and delete_py:
            if os.path.exists(abs_path):
                try:
                    os.remove(abs_path)
                except Exception:
                    pass

    build_folder_path = os.path.join(root_path, 'build')
    if os.path.exists(build_folder_path):
        try:
            shutil.rmtree(build_folder_path)
        except Exception:
            pass

    setup_path = os.path.join(root_path, 'setup.py')
    if os.path.exists(setup_path):
        try:
            os.remove(setup_path)
        except Exception:
            pass


def compile_batch(root_path, files_rel, nthreads):
    if not files_rel:
        return True

    cwd = os.getcwd()
    os.chdir(root_path)
    try:
        build_temp = os.path.join(root_path, "build", "temp")
        build_lib = os.path.join(root_path, "build", "lib")
        ensure_build_dirs(root_path, files_rel, build_temp=build_temp, build_lib=build_lib)
        ensure_inplace_output_dirs(root_path, files_rel)
        ext_modules = cythonize(
            files_rel,
            compiler_directives={
                "language_level": 3,
                "c_string_encoding": "utf-8",
            },
            nthreads=nthreads
        )
        try:
            setup(
                name='global_build',
                ext_modules=ext_modules,
                script_args=[
                    "build_ext",
                    "--inplace",
                    "--build-temp",
                    build_temp,
                    "--build-lib",
                    build_lib,
                ],
            )
        except SystemExit as e:
            if e.code != 0:
                log(f"批量编译失败，返回码: {e.code}", also_print=True)
            return e.code == 0
        fix_nested_inplace_outputs(root_path)
        return True
    except Exception as e:
        log(f"批量编译失败: {e}", also_print=True)
        return False
    finally:
        os.chdir(cwd)


def compile_single(root_path, file_rel, nthreads):
    ok = compile_batch(root_path, [file_rel], nthreads)
    return ok


def ensure_build_dirs(root_path, files_rel, build_temp=None, build_lib=None):
    try:
        temp_dir = build_temp or os.path.join(root_path, "build", "temp")
        lib_dir = build_lib or os.path.join(root_path, "build", "lib")
        release_dir = os.path.join(temp_dir, "Release")
        debug_dir = os.path.join(temp_dir, "Debug")
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(lib_dir, exist_ok=True)
        os.makedirs(release_dir, exist_ok=True)
        os.makedirs(debug_dir, exist_ok=True)
        prefix_rel = None
        parts = Path(root_path).parts
        for marker in ("Src", "Gui", "UpdaterSet"):
            if marker in parts:
                idx = parts.index(marker)
                prefix_rel = os.path.join(*parts[idx:])
                break
        for rel_path in files_rel:
            rel_dir = os.path.dirname(rel_path)
            if rel_dir:
                os.makedirs(os.path.join(temp_dir, rel_dir), exist_ok=True)
                os.makedirs(os.path.join(lib_dir, rel_dir), exist_ok=True)
                os.makedirs(os.path.join(release_dir, rel_dir), exist_ok=True)
                os.makedirs(os.path.join(debug_dir, rel_dir), exist_ok=True)
                if prefix_rel:
                    prefixed = os.path.join(prefix_rel, rel_dir)
                    os.makedirs(os.path.join(temp_dir, prefixed), exist_ok=True)
                    os.makedirs(os.path.join(lib_dir, prefixed), exist_ok=True)
                    os.makedirs(os.path.join(release_dir, prefixed), exist_ok=True)
                    os.makedirs(os.path.join(debug_dir, prefixed), exist_ok=True)
    except Exception:
        pass


def _get_prefix_rel(root_path):
    parts = Path(root_path).parts
    for marker in ("Src", "Gui", "UpdaterSet"):
        if marker in parts:
            idx = parts.index(marker)
            return os.path.join(*parts[idx:])
    return None


def ensure_inplace_output_dirs(root_path, files_rel):
    try:
        prefix_rel = _get_prefix_rel(root_path)
        for rel_path in files_rel:
            rel_dir = os.path.dirname(rel_path)
            if rel_dir:
                os.makedirs(os.path.join(root_path, rel_dir), exist_ok=True)
                if prefix_rel:
                    os.makedirs(os.path.join(root_path, prefix_rel, rel_dir), exist_ok=True)
            elif prefix_rel:
                os.makedirs(os.path.join(root_path, prefix_rel), exist_ok=True)
    except Exception:
        pass


def fix_nested_inplace_outputs(root_path):
    try:
        prefix_rel = _get_prefix_rel(root_path)
        if not prefix_rel:
            return
        nested_root = os.path.join(root_path, prefix_rel)
        if not os.path.isdir(nested_root):
            return
        for src_file in [
            os.path.join(root, file)
            for root, _, files in os.walk(nested_root)
            for file in files
            if file.endswith(".pyd")
        ]:
            rel_path = os.path.relpath(src_file, nested_root)
            dst_file = os.path.join(root_path, rel_path)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.move(src_file, dst_file)
        try:
            shutil.rmtree(nested_root)
        except Exception:
            pass
    except Exception:
        pass


def compile_all(root_path, del_py, skip_dirs, nthreads):
    files_rel = []
    start_time = time.perf_counter()
    try:
        files_rel = collect_py_files(root_path, skip_dirs)
        total_files = len(files_rel)
        if total_files == 0:
            return True
        preview_count = min(10, total_files)
        preview_list = ", ".join(files_rel[:preview_count])
        msg = f"待编译文件数: {total_files}"
        if preview_list:
            msg += f"；示例: {preview_list}"
        if total_files > preview_count:
            msg += " ..."
        log(msg, also_print=True)
        emit_count(0, total_files)
        emit_progress(5)
        for idx, rel_path in enumerate(files_rel, start=1):
            add_cython_directive(os.path.join(root_path, rel_path))
            emit_count(idx, total_files)
            emit_progress(5 + (20 * idx / total_files))
        emit_progress(25)

        ok = compile_batch(root_path, files_rel, nthreads)
        if ok:
            emit_count(total_files, total_files)
            emit_progress(80)
            cleanup_build_files(root_path, files_rel, del_py, delete_py=True)
            emit_progress(100)
            total_seconds = time.perf_counter() - start_time
            emit_total_time(total_seconds)
            log(f"目录编译完成: {root_path}, 文件数: {len(files_rel)}, 耗时: {total_seconds:.2f}s", also_print=True)
            return True

        # 回退到逐文件编译以记录失败文件
        for idx, rel_path in enumerate(files_rel, start=1):
            single_ok = compile_single(root_path, rel_path, nthreads)
            if not single_ok:
                record_failed_file(os.path.join(root_path, rel_path))
            cleanup_build_files(root_path, [rel_path], del_py, delete_py=single_ok)
            emit_progress(100 * idx / len(files_rel))
            emit_count(idx, total_files)
        total_seconds = time.perf_counter() - start_time
        emit_total_time(total_seconds)
        log(f"目录编译回退完成: {root_path}, 文件数: {len(files_rel)}, 耗时: {total_seconds:.2f}s", also_print=True)
        return False
    finally:
        restore_init_files(root_path, skip_dirs)


def compile_one(file_path, del_py, nthreads):
    start_time = time.perf_counter()
    root_path = os.path.dirname(file_path)
    file_rel = os.path.basename(file_path)
    add_cython_directive(file_path)
    emit_count(0, 1)
    emit_progress(10)
    ok = compile_single(root_path, file_rel, nthreads)
    if not ok:
        record_failed_file(file_path)
    emit_progress(90)
    emit_count(1, 1)
    cleanup_build_files(root_path, [file_rel], del_py, delete_py=ok)
    emit_progress(100)
    total_seconds = time.perf_counter() - start_time
    emit_total_time(total_seconds)
    status = "成功" if ok else "失败"
    log(f"单文件编译{status}: {file_path}, 耗时: {total_seconds:.2f}s", also_print=True)
    return ok


if __name__ == "__main__":
    if len(sys.argv) <= 3:
        log("命令行参数错误...", also_print=True)
        sys.exit()

    one_all, del_py, paths, env = sys.argv[1:5]

    skip_dirs = []
    if len(sys.argv) > 5:
        skip_str = sys.argv[5]
        if skip_str and skip_str.strip():
            skip_dirs = skip_str.split(',')

    config_skip_dirs = load_skip_dirs_from_config(paths)
    merged_skip_dirs = list({d for d in (skip_dirs + config_skip_dirs) if d})
    if merged_skip_dirs:
        log(f"跳过的文件夹: {merged_skip_dirs}", also_print=True)

    nthreads = load_compile_threads_from_config() or (os.cpu_count() or 4)

    if one_all == 'one':
        compile_one(paths, del_py, nthreads)
    else:
        compile_all(paths, del_py, merged_skip_dirs, nthreads)
