# Python 打包工具 (Packet Py Project)

> 一款基于 PyQt5 的 Python 项目打包工具，提供图形化界面辅助将 Python 项目打包为独立可执行文件（exe），并支持代码加密。

## 📋 项目简介

本工具旨在简化 Python 项目的打包流程，通过友好的 GUI 界面管理项目、环境和打包配置，支持以下核心功能：

- **自动化打包**：使用 Nuitka 将 Python 项目编译为独立的 exe 文件
- **代码加密**：使用 Cython 将 .py 文件编译为 .pyd 文件，保护源代码
- **环境管理**：支持打包和管理多个 Python 环境，自动集成到可执行文件中
- **可视化配置**：通过 GUI 界面配置项目图标、文件夹复制、跳过目录等选项
- **增量编译**：支持仅编译 Git 修改的文件，提升开发效率

## ✨ 主要功能

### 1. 环境管理
- 添加 Python 环境（conda/venv）并自动压缩为 zip
- 删除已添加的环境
- 环境自动解压到打包目录，实现完全独立运行

### 2. 项目配置
- 选择项目主文件（.py）
- 配置应用程序图标（.ico）
- 指定需要复制到打包目录的文件夹
- 设置打包时跳过的目录

### 3. 打包功能
- **测试模式**：保留控制台输出，便于调试
- **正式模式**：无控制台窗口，设置自定义图标
- 支持 PyQt5 插件自动识别
- 进度条实时显示打包进度

### 4. 代码加密
- 批量将 .py 文件编译为 .pyd 文件
- 支持全量加密和增量加密（仅编译修改的文件）
- 自动跳过 `__init__.py` 和指定的特殊文件
- 支持 Git 集成，自动识别未暂存的修改文件

## 🛠️ 技术栈

- **Python 3.8+**
- **PyQt5**：图形界面
- **Nuitka**：Python 到 exe 编译器
- **Cython**：Python 到 C/pyd 编译器
- **Git**：版本控制集成

## 📦 安装依赖

### 1. 安装 Python 依赖

```bash
pip install PyQt5
pip install cython
pip install nuitka
```
在要打包的虚拟环境中安装
cython
nuitka
### 2. 安装 MinGW64（Nuitka 编译需要）

- 下载并安装 MinGW64
- 将 MinGW64 的 bin 目录添加到系统环境变量 PATH

### 3. 配置 Nuitka 路径

在 `Src/manager/nuitkaManager.py` 中配置你的 Nuitka 路径：

```python
nuitka_executable = r"你的Python环境\Scripts\nuitka.bat"
```

## 🚀 使用方法

### 启动应用

```bash
python StartApp.py
```

### 打包流程

1. **添加环境**
   - 点击"环境"标签页
   - 点击"添加环境"，选择你的 Python 环境目录（如 conda 环境）
   - 工具会自动压缩环境并保存到 `PyZip` 目录

2. **配置项目**
   - 在"打包"标签页点击"选择主文件"，选择项目的主 .py 文件
   - 点击"选择图标"，选择应用程序图标（.ico 文件）
   - 点击"选择要复制的文件夹"，添加需要打包的资源目录
   - 点击"保存要复制的文件夹"保存配置

3. **开始打包**
   - 在项目列表中选择要打包的项目
   - 在环境列表中选择使用的 Python 环境
   - 点击"开始打包"按钮
   - 等待打包完成，查看进度条和日志输出

4. **代码加密（可选）**
   - 选择项目和环境
   - 点击"编译"标签页
   - 点击"加密"按钮，将源代码编译为 pyd 文件

### 增量编译

1. 在"部分编译"标签页选择项目和环境
2. 点击"刷新修改文件"，自动识别 Git 未暂存的修改文件
3. 点击"部分编译"，仅编译修改的文件

## 📂 项目结构

```
packet_py_project/
├── StartApp.py              # 应用程序启动入口
├── packet.py                # Nuitka 打包脚本（命令行版本）
├── py2pyd.py                # Cython 批量编译工具（命令行版本）
├── Src/                     # 源代码目录
│   ├── Window.py            # 主窗口实现
│   ├── mainWindow.py        # UI 界面定义（由 .ui 生成）
│   ├── mainWindow.ui        # Qt Designer 界面文件
│   ├── config.json          # 配置文件
│   └── manager/             # 功能管理器模块
│       ├── SignalManager.py      # 信号管理器
│       ├── configManager.py      # 配置管理器
│       ├── encryptManager.py     # 加密管理器
│       ├── nuitkaManager.py      # Nuitka 打包管理器
│       ├── zipManager.py         # 压缩管理器
│       └── unZipManager.py       # 解压管理器
├── PyZip/                   # 环境压缩包存储目录
├── midDir/                  # 临时中间文件目录
└── README.md                # 项目说明文档
```

## ⚠️ 注意事项

1. **路径配置**
   - 在 `packet.py` 和 `Src/manager/nuitkaManager.py` 中配置正确的 Nuitka 路径
   - 确保路径中不包含中文或特殊字符

2. **环境要求**
   - Python 3.8 或更高版本
   - Windows 操作系统（Nuitka 在 Windows 上表现最佳）
   - 至少 4GB 可用磁盘空间（用于环境压缩和打包）

3. **打包大小**
   - 集成完整 Python 环境后，打包文件可能较大（100MB+）
   - 建议只添加项目必需的环境依赖

4. **代码加密限制**
   - `__init__.py` 文件不会被编译
   - 部分动态加载的代码可能在加密后失效
   - 建议在加密前充分测试

5. **Git 集成**
   - 增量编译功能依赖 Git，确保项目在 Git 仓库中
   - 确保 Git 已配置 `core.quotepath false` 以支持中文文件名

## 🔧 开发说明

### 修改 UI 界面

1. 使用 Qt Designer 打开 `Src/mainWindow.ui`
2. 修改界面布局和控件
3. 使用以下命令重新生成 Python 代码：

```bash
pyuic5 -o Src/mainWindow.py Src/mainWindow.ui
```

### 独立使用命令行工具

**Nuitka 打包（packet.py）**：
```python
# 修改 packet.py 中的配置
new_directory = r"你的项目路径"
main_file = "主文件.py"
# 运行
python packet.py
```

**Cython 编译（py2pyd.py）**：
```bash
# 编译单个文件
python py2pyd.py one nodel 文件路径.py 你的Python环境路径

# 批量编译目录
python py2pyd.py all del 目录路径 你的Python环境路径
```

## 📝 更新日志

- **2024-12-10**：初始版本发布
  - 实现基础打包功能
  - 支持环境管理和代码加密
  - 集成 Git 增量编译

## 📄 许可证

本项目仅供学习和个人使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 Issue 反馈。
