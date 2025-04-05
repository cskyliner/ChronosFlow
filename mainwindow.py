from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QPushButton, QSplitter, QWidget
from PySide6.QtCore import Qt

class UiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TODO List")
        # 设置主页面和侧边栏的分割器 TODO：调试分割时候的最小与最大值
        self.splitter = QSplitter(Qt.Horizontal,self)
        self.setCentralWidget(self.splitter)
        # TODO：设置主窗口，可能需要存储切换多个窗口
        self.main_widget = QWidget(self)

        # TODO：侧边栏上功能按钮的布局
        self.sidebar = QWidget(self)
        self.sidebar.setStyleSheet("background-color: lightgray;")

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.main_widget)
        self.splitter.setStretchFactor(0, 1)  # 侧边栏的伸缩因子
        self.splitter.setStretchFactor(1, 10)  # 主内容的伸缩因子

        # 创建菜单按钮 TODO：菜单按钮的图标和位置
        menu_button = QPushButton("Sidebar",self)
        # 连接菜单按钮和侧边栏展示
        menu_button.clicked.connect(self.fold_sidebar)

    def fold_sidebar(self) -> None:
        """
        control the sidebar
        TODO：侧边栏的打开和关闭动效
        :return: None
        """
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.splitter.setStretchFactor(1, 1)
        else:
            self.sidebar.show()
            self.splitter.setStretchFactor(1, 10)
        self.splitter.update()
        print("Control Sidebar successfully!")