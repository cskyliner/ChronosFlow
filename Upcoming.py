from common import *
from Emitter import Emitter
from functools import partial


class CustomListItem(QWidget):
	"""一条日程"""

	def __init__(self, theme, is_even_row, parent=None):
		""":param is_even: 判断奇偶，斑马线效果"""
		super().__init__(parent)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setStyleSheet(f"""
		            CustomListItem {{
		                background-color: transparent;
		                border-radius: 4px;
		            }}
		            CustomListItem:hover {{
		                background-color: palette(midlight); /*轻微高亮*/
		            }}
		        """)

		# 设置消息布局
		layout = QHBoxLayout(self)
		layout.setContentsMargins(5, 2, 5, 2)  # 边距：左、上、右、下

		# 左侧为是否完成的复选框 TODO:打勾后发信号
		self.finish_checkbox = QCheckBox()
		self.finish_checkbox.toggled.connect(partial(self.this_is_finished))
		layout.addWidget(self.finish_checkbox)

		# 字体
		font = QFont()
		font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
		font.setPointSize(13)
		font1 = QFont()  # 用于‘+’的字体
		font1.setPointSize(18)

		# 展示主题的标签
		self.theme_display_label = QLabel(f"{theme}")
		self.theme_display_label.setFont(font)
		layout.addWidget(self.theme_display_label)

		# 弹性空白区域（将右侧按钮推到最右）
		spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
		layout.addItem(spacer)

		# 右侧为event，是一个按钮，只显示+，在点击后会跳转到Schedule页面，显示详细内容 TODO：跳转
		self.theme_display_button = QPushButton("+")
		self.theme_display_button.setStyleSheet("""
		                QPushButton {
		                    background-color: transparent;
		                    border: none;
		                    padding: 25px;
		                    qproperty-alignment: 'AlignCenter';
		                    color: palette(mid); /*中等颜色*/
		                }
		                QPushButton:hover {
		                    color: #07C160;
		                }
		                QPushButton:pressed {
							color: #05974C;
						}
		            """)
		self.theme_display_button.setFont(font1)
		self.theme_display_button.clicked.connect(
			partial(Emitter.instance().send_page_change_signal, name="Schedule"))
		self.theme_display_button.clicked.connect(
			self.send_message)  # TODO:传递具体信息（哈希依据），以便跳转到相应的CreateEvent界面；如何将该信息传递给CreateEvent界面

		layout.addWidget(self.theme_display_button)

	def this_is_finished(self):
		# TODO:通知后端
		pass

	def send_message(self):
		pass


class Upcoming(QListWidget):
	"""
	容纳多个SingleUpcoming，有滚动等功能
	"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setSelectionMode(QListWidget.NoSelection)  # 禁用选中高亮

		# TODO:触底时接连获取
		for i in range(10):
			custom_widget = CustomListItem(self.get_theme(), (i % 2 == 0))  # 暂时的写法
			item = QListWidgetItem()
			item.setSizeHint(custom_widget.sizeHint())  # 设置合适的大小
			self.addItem(item)
			self.setItemWidget(item, custom_widget)

	def get_theme(self):
		"""从后端获取主题"""
		# TODO
		return "theme"
