from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import QDate


class Calendar(QCalendarWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.hover_date = QDate()
		self.setMouseTracking(True)

		self.setStyleSheet("""
		            Calendar QAbstractItemView:enabled {     /*禁用选中高亮效果*/
		                selection-background-color: transparent;  /* 透明背景 */
		                selection-color: palette(text);        /* 使用正常文本颜色 */
		            }
		            QCalendarWidget QAbstractItemView {   /*消除边框*/
		                border: none;
		                outline: 0;
		                selection-background-color: transparent;
		            }
		            QCalendarWidget QAbstractItemView:item:hover {  /*鼠标悬停*/
		                background-color: palette(midlight);
		            }
		        """)