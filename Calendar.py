from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import QDate

class Calendar(QCalendarWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		# 消除边框
		self.setStyleSheet("""
		            QCalendarWidget QAbstractItemView {
		                border: none;
		                outline: 0;
		                selection-background-color: transparent;
		            }
		        """)

		# 实现鼠标悬停效果
		self.hover_date = QDate()
		self.setMouseTracking(True)
		self.setStyleSheet("""
		            QCalendarWidget QAbstractItemView:item:hover {
		                background-color: #d0d0d0;
		            }
		        """)
