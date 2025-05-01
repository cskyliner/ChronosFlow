from common import *

class SingleUpcoming(QWidget):
	"""
	一条日程
	"""

	def __init__(self, parent=None):
		super().__init__(parent)

		# 设置消息布局
		layout = QHBoxLayout(self)
		layout.setContentsMargins(10, 5, 10, 5)

		# 左侧为是否完成的复选框 TODO:打勾后
		self.finish_checkbox = QCheckBox()
		layout.addWidget(self.finish_checkbox)

		# 右侧为event，是一个按钮，只显示主题，在点击后会跳转到Schedule页面，显示详细内容 TODO：跳转
		self.theme_display_button = QPushButton("1")
		self.theme_display_button.setStyleSheet("""
		    QPushButton {
		        background-color: transparent;
                border: none;
		        padding: 5px;
		        qproperty-wordWrap: true; /*自动换行*/
		    }
		    QPushButton:hover {
                background-color: #d0d0d0;
                border-radius: 4px;
            }
            QPushButton:pressed {
				background-color: #e0e0e0;
			}
		""")
		layout.addWidget(self.theme_display_button)


class Upcoming(QListWidget):
	"""
	容纳多个SingleUpcoming，有滚动等功能
	"""

	def __init__(self, parent=None):
		super().__init__(parent)

		custom_widget=SingleUpcoming()
		item = QListWidgetItem()
		item.setSizeHint(custom_widget.sizeHint())  # 设置合适的大小
		self.addItem(item)
		self.setItemWidget(item, custom_widget)
