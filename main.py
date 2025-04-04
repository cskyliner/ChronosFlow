from PySide6.QtWidgets import QApplication
from mainwindow import UiMainWindow

if __name__ == "__main__":
        """
        this is the entrance point of the application
        """
        app = QApplication([])
        window = UiMainWindow()
        window.show()
        app.exec()