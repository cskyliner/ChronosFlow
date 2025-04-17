from PySide6.QtWidgets import QApplication, QStyleFactory
from MainWindow import MainWindow
from PySide6.QtGui import QIcon
import sys
def init_platform_style(a):
	#根据系统选择UI风格
	if sys.platform == "win32":
		a.setStyle(QStyleFactory.create("windows"))
	elif sys.platform == "darwin":
		a.setStyle(QStyleFactory.create("macintosh"))
	elif sys.platform.startswith("linux"):
		a.setStyle(QStyleFactory.create("fusion"))
if __name__ == "__main__":
	app = QApplication([])
	init_platform_style(app)
	app.setWindowIcon(QIcon("/pic/todolist.png"))
	main_window = MainWindow(1000, 600, 140, 100)
	main_window.show()
	app.exec()
