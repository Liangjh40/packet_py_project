"""
======================
@FileName: SignalManager
@Author: ZhuBiao
@Company: BayOne
@CreateFileTime:2023/11/29 19:34
@Explain: 信号管理
=====================
"""
from PyQt5.QtCore import QObject, pyqtSignal

class SignalManager(QObject):

    updateProgressBarValueSignal = pyqtSignal(int)
    messageBoxSignal = pyqtSignal(str)
    updatePartEncryptTextSignal = pyqtSignal(str, str)


signal_manager = SignalManager()