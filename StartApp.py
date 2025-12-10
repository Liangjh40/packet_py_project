import sys
from PyQt5.QtWidgets import QApplication

from Src.Window import MainWindow

def run():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

run()