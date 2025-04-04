from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QPushButton

class UiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TODO List")
        # 创建菜单按钮
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("View")
        # 实现菜单弹出侧边栏动作
        menu_show_sidebar = QAction("Show Sidebar", self)
        menu_show_sidebar.trigger(self.show_sidebar)
        self.button = QPushButton("Click Me as Test", self)
        self.button.clicked.connect(self.on_button_click)
        
    def on_button_click(self):
        print("Button clicked successfully!")

    def show_sidebar(self):
        print("Show Sidebar clicked successfully!")