import sys
from PyQt5.QtWidgets import QApplication

from Src.Window import MainWindow

import os

# # 移除环境变量干扰
# if "QT_QPA_PLATFORM_PLUGIN_PATH" in os.environ:
#     os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")

def run():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

run()