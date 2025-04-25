# 在 MainWindow.py 中测试
from PySide6.QtWidgets import QApplication
from Settings import SettingsPage
if __name__  == "__main__":
    app = QApplication([])
    settings = SettingsPage()
    settings.show()
    app.exec()