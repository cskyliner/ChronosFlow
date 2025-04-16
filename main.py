from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow

if __name__ == "__main__":
	app = QApplication([])
	main_window = MainWindow(1000, 600, 140, 100)
	main_window.show()
	app.exec_()