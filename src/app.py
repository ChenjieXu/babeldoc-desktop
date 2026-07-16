"""
BabelDOC Desktop - 主应用类
"""

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


class BabelDocApp:
    """主应用类"""

    def __init__(self, app: QApplication):
        self.app = app
        self.main_window = MainWindow()

    def show(self):
        """显示主窗口"""
        self.main_window.show()
