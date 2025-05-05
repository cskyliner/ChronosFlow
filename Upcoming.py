from common import *
from Emitter import Emitter
from functools import partial

logger = logging.getLogger("Upcoming")


class CustomListItem(QWidget):
	"""一条日程"""

	def __init__(self, theme, parent=None):
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

		self.themes = []  # 临时写法，存贮从后端得到的数据TODO:不一定要用列表，要看后端传入哪些信息
		self.loading_finished = False  # 是否加载完成

		self.get_data()
		self.load_more_data()

		self.verticalScrollBar().valueChanged.connect(self.check_scroll)  # 检测是否滚动到底部

	def check_scroll(self):
		"""检查是否滚动到底部"""
		if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
			self.show_loading_label()

	def show_loading_label(self):
		item = QListWidgetItem("Loading……")
		item.setTextAlignment(Qt.AlignCenter)
		self.addItem(item)
		QTimer.singleShot(1000, self.load_more_data)
		self.get_data()  # 同时向后端请求数据TODO:必须保证在上一行设定时间内完成,否则会在load_more_data中报错;也可以设计成load_more_data先挂起，加载完成之后发信号？

	def get_data(self):
		"""从后端加载数据"""# TODO:从后端获取10个;以下为临时写法
		self.themes = [f"theme{i}" for i in range(10)]
		self.loading_finished = True

	def load_more_data(self):
		"""将数据添加到self"""
		if self.count() > 0:
			self.takeItem(self.count() - 1)  # 删除loading

		if self.loading_finished:
			for theme in self.themes:
				custom_widget = CustomListItem(f"{theme}")
				item = QListWidgetItem()
				item.setSizeHint(custom_widget.sizeHint())  # 设置合适的大小
				self.addItem(item)
				self.setItemWidget(item, custom_widget)
			self.loading_finished = False
		else:
			logger.error("数据加载未完成！")
