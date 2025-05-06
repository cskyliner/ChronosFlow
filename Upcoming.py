from common import *
from Emitter import Emitter
from functools import partial
from Event import BaseEvent
log = logging.getLogger("Upcoming")


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
			self.send_message)  # TODO:传递对应id，以便跳转到相应的CreateEvent界面；如何将该信息传递给CreateEvent界面

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

		self.events:list[BaseEvent] = []  		# 存贮从后端得到的数据
		self.loading = False  					# 是否正在加载
		self.no_more_events = False				# 是否显示全部数据
		self.event_num = 0 						# 记录当前个数，传给后端提取数据
		self.page_num = 10 						# 每页显示的事件数
		self.loading_item = None				# 加载标签
		self.load_more_data()

		self.verticalScrollBar().valueChanged.connect(self.check_scroll)  # 检测是否滚动到底部

	def check_scroll(self):
		"""检查是否滚动到底部"""
		if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
			if not self.loading and not self.no_more_events:
				self.load_more_data()
			elif self.loading:
				log.info("正在加载数据，请稍等……")
			elif self.no_more_events:
				log.info("没有更多数据了，停止加载……")
			else:
				log.error("未知错误，无法加载数据")

	def show_loading_label(self):
		self.loading_item = QListWidgetItem("Loading……")
		self.loading_item.setTextAlignment(Qt.AlignCenter)
		self.addItem(self.loading_item)
		# self.get_data()

	def get_data(self,data:tuple[BaseEvent]=None):
		"""从后端加载数据"""
		if data is not None and len(data) > 0:
			log.info(f"接收数据成功，共接收 {len(data)} 条数据：\n" + 
         "\n".join(f"- {event.title} @ {event.datetime}" for event in data))
			self.events.extend(data)
			self.event_num += len(data)
		else:
			log.info("接受数据为空，无更多数据")
			# 数据加载完毕
			self.no_more_events = True
		# 删除加载标签
		if hasattr(self, "loading_item"):
			self.takeItem(self.row(self.loading_item))
			del self.loading_item

	def load_more_data(self):
		"""将数据添加到self"""
		# 连接接收信号
		Emitter.instance().backend_data_to_frontend_signal.connect(self.get_data)
		# 显示加载标签
		self.show_loading_label()
		# 发送请求信号
		Emitter.instance().request_update_upcoming_event_signal(self.event_num, self.page_num)
		# 断开接收信号连接
		Emitter.instance().backend_data_to_frontend_signal.disconnect(self.get_data)
		# 停止加载
		self.loading = False
		if self.no_more_events:
			log.info("没有更多数据了，停止加载……")
			return
		for event in self.events:
			custom_widget = CustomListItem(f"{event.title}")
			item = QListWidgetItem()
			item.setSizeHint(custom_widget.sizeHint())  # 设置合适的大小
			self.addItem(item)
			self.setItemWidget(item, custom_widget)
