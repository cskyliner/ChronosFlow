from common import *
from SideBar import SideBar
from Calendar import Calendar
from functools import partial
from CreateEventWindow import Schedule
from Emitter import Emitter
from Settings import SettingsPage
from Tray import Tray
from FloatingWindow import FloatingWindow
from Notice import Notice
from Upcoming import Upcoming, FloatingButton
from FontSetting import set_font
from Event import DDLEvent, get_events_in_month, BaseEvent

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):

	def __init__(self, app, width=1000, height=600):
		super().__init__()
		self.setWindowTitle("ChronosFlow")
		# self.main_window_calendar = None

		# 获取屏幕尺寸，设置主窗口位置
		self.resize(width, height)
		screen_geometry = app.primaryScreen().availableGeometry()
		self.move(screen_geometry.width() // 2 - width // 2, screen_geometry.height() // 2 - height // 2)

		# 动画管理集
		self.animations: dict[str, QPropertyAnimation] = {}

		# 主窗口中心部件（容纳 main_layout）
		self.central_widget = QWidget()
		self.setCentralWidget(self.central_widget)

		# 主布局 main_layout（容纳侧边栏和主窗口）
		self.main_layout = QHBoxLayout()
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.setSpacing(0)
		self.central_widget.setLayout(self.main_layout)

		# 侧边栏
		self.sidebar = SideBar(self)
		self.sidebar.setMaximumWidth(230)  # 设置初始宽度为230
		self.main_layout.addWidget(self.sidebar)
		self.sidebar_visible = True  # 初始化侧边栏状态
		self.setup_sidebar_animation()

		# 主窗口（设计为堆叠窗口，有多个界面）
		self.main_stack = QStackedWidget()
		self.main_stack.setStyleSheet("""
							QStackedWidget{
									background-image: url("local_data/1.jpg");  /* 图片路径 */
									background-position: center;    /* 居中 */
									background-repeat: no-repeat;   /* 不重复 */
									background-size: contain;       /* 保持比例 */
									}
								""")
		self.main_layout.addWidget(self.main_stack)

		# 连接sidebar的信号
		Emitter.instance().page_change_signal.connect(partial(self.navigate_to, stack=self.main_stack, date=None))
		# 通过名称记录页面，使用字典双向映射
		self.main_stack_map = {}  # 名称→索引

		# 设置 main_stack各页面的内容，注意初始化顺序
		self.setup_main_window()  # 日历窗口（主界面）
		self.setup_create_event_window()  # 日程填写窗口
		self.setup_setting_window()  # 设置界面
		self.setup_upcoming_window()  # 日程展示窗口

		# TODO:更改日历加载事件逻辑，通过向后端发送时间端请求事件，不要耦合upcoming完成
		cur_month = QDate.currentDate().month()
		cur_year = QDate.currentDate().year()
		self.get_events_in_month_from_backend(cur_year, cur_month)
		# self.load_event_in_calendar(self.upcoming.events)
		# 初始化通知系统
		self.notice_system = Notice()
		# 用于在通知时自动显示悬浮窗
		self.notice_system.notify_show_floating_window.connect(self.show_floating_window)

		# 初始化托盘
		self.tray = None
		self._init_tray()

		# 悬浮窗口初始化
		self._init_floating_window()

		# 安装事件过滤器，处理Calendar页面的侧边栏的收放
		self.main_stack.installEventFilter(self)
		self.search_column.installEventFilter(self)
		self.search_edit.installEventFilter(self)

	# 或许可以有
	# self.setWindowIcon(QIcon(self._get_icon_path()))

	def setup_main_window(self):
		"""
		main_window创建
		"""
		self.main_window = QWidget()
		main_window_layout = QVBoxLayout()  # 内容区域布局
		main_window_layout.setSpacing(5)  # 设置相邻控件间距为0
		main_window_layout.setContentsMargins(20, 5, 20, 20)
		self.main_window.setLayout(main_window_layout)

		upper_layout = QHBoxLayout()
		upper_layout.setSpacing(0)
		# 添加'<'按钮
		sidebar_btn = QPushButton("<")
		sidebar_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    padding: 0;
		    						margin: 0;
				                    text-align: center;
				                    color: #a0a0a0;
				                }
				                QPushButton:hover {
				                    color: #07C160;
				                }
				                QPushButton:pressed {
									color: #05974C;
								}
				            """)
		set_font(sidebar_btn, 1)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 添加search文本框
		# 左侧文本框
		self.search_edit = QLineEdit()
		self.search_edit.setPlaceholderText("搜索")
		set_font(self.search_edit)
		self.search_edit.setStyleSheet("""
								    QLineEdit {
								    background: transparent;
						            padding: 8px;
					                border: 1px solid palette(mid);
					                border-top-left-radius: 19px;     /* 左上角 */
    								border-top-right-radius: 0px;    /* 右上角 */
    								border-bottom-left-radius: 19px;  /* 左下角 */
    								border-bottom-right-radius: 0px; /* 右下角 */
					                font-size: 14px;
						            }
							    """)
		self.search_edit.setFixedHeight(38)

		# 回车触发搜索功能
		self.search_edit.returnPressed.connect(self.get_search_result)

		# 右侧按钮
		btn = QPushButton()
		btn.setIcon(QIcon.fromTheme("system-search"))
		btn.setStyleSheet("""
					QPushButton {
		                background-color: transparent;
		                border: 1px solid palette(mid);
		                border-top-left-radius: 0px;     /* 左上角 */
    					border-top-right-radius: 19px;    /* 右上角 */
    					border-bottom-left-radius: 0px;  /* 左下角 */
    					border-bottom-right-radius: 19px; /* 右下角 */
		                padding: 25px;
		                text-align: center;
		            }
		            QPushButton:hover {
		                background-color: palette(midlight);
		            }
		            QPushButton:pressed {
						background-color: palette(mid);
					}
				""")
		btn.setFixedSize(38, 38)
		btn.clicked.connect(self.get_search_result)

		upper_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
		upper_layout.addItem(spacer)
		upper_layout.addWidget(self.search_edit)
		upper_layout.addWidget(btn)
		main_window_layout.addLayout(upper_layout)

		middle_layout = QHBoxLayout()
		# 创建日历界面
		self.main_window_calendar = Calendar()
		self.main_window_calendar.setGridVisible(False)
		self.main_window_calendar.clicked.connect(
			lambda date: self.navigate_to("Schedule", self.main_stack, date))  # 点击日历时跳转到 schedule
		# 右侧搜索栏
		self.search_column = Upcoming(1)
		self.search_column.setMaximumWidth(0)
		self.main_layout.addWidget(self.search_column)
		self.search_column_visible = False
		self.setup_search_column_animation()

		middle_layout.addWidget(self.main_window_calendar)
		middle_layout.addWidget(self.search_column)
		main_window_layout.addLayout(middle_layout)

		# 创建悬浮按钮
		float_btn = FloatingButton(self.main_window)
		float_btn.move(50, 50)  # 初始位置
		float_btn.raise_()  # 确保在最上层
		float_btn.clicked.connect(partial(self.navigate_to, "Schedule", self.main_stack))

		self.add_page(self.main_stack, self.main_window, "Calendar")  # main_window是日历，故名为Calendar

	def setup_create_event_window(self):
		"""
		创建 create_event_window
		"""
		self.create_event_window = QWidget()

		schedule_layout = QVBoxLayout()  # 内容区域布局
		schedule_layout.setSpacing(0)
		schedule_layout.setContentsMargins(20, 5, 20, 20)
		self.create_event_window.setLayout(schedule_layout)

		btn_layout = QHBoxLayout()
		btn_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
		schedule_layout.addLayout(btn_layout)

		sidebar_btn = QPushButton("<")
		sidebar_btn.setStyleSheet("""
								QPushButton {
								background-color: transparent;
								border: none;
								padding: 0;
								margin: 0;
								text-align: center;
								color: #a0a0a0;
								}
								QPushButton:hover {
								color: #07C160;
								}
								QPushButton:pressed {
								color: #05974C;
								}
								""")
		set_font(sidebar_btn)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setStyleSheet("""
						        QPushButton {
						        background-color: transparent;
						        border: none;
						        padding: 0;
				    			margin: 0;
						        text-align: center;
						        color: #a0a0a0;
						        }
						        QPushButton:hover {
								color: rgb(235,51,36);
								}
								QPushButton:pressed {
								color: rgb(189,41,29);
								}
						        """)
		set_font(return_btn, 1)
		return_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))

		btn_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		btn_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)
		# 创建Schedule
		self.schedule = Schedule()
		schedule_layout.addWidget(self.schedule)
		self.add_page(self.main_stack, self.create_event_window, "Schedule")

	def setup_setting_window(self):
		"""创建设置栏"""
		self.setting_window = QWidget()
		setting_layout = QVBoxLayout()  # 内容区域布局
		setting_layout.setSpacing(0)
		setting_layout.setContentsMargins(20, 5, 20, 20)
		self.setting_window.setLayout(setting_layout)

		btn_layout = QHBoxLayout()
		btn_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
		setting_layout.addLayout(btn_layout)

		sidebar_btn = QPushButton("<")
		sidebar_btn.setStyleSheet("""
								QPushButton {
								background-color: transparent;
								border: none;
								padding: 0;
								margin: 0;
								text-align: center;
								color: #a0a0a0;
								}
								QPushButton:hover {
								color: #07C160;
								}
								QPushButton:pressed {
								color: #05974C;
								}
						            """)
		set_font(sidebar_btn)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    padding: 0;
		    						margin: 0;
				                    text-align: center;
				                    color: #a0a0a0;
				                }
				                QPushButton:hover {
								color: rgb(235,51,36);
								}
								QPushButton:pressed {
								color: rgb(189,41,29);
								}
				            """)
		set_font(return_btn, 1)
		return_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))

		btn_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		btn_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)

		self.setting = SettingsPage()
		setting_layout.addWidget(self.setting)
		self.add_page(self.main_stack, self.setting_window, "Setting")

	def setup_upcoming_window(self):
		"""日程展示窗口"""
		self.upcoming_window = QWidget()

		layout = QVBoxLayout()  # 内容区域布局
		layout.setSpacing(0)
		layout.setContentsMargins(20, 5, 20, 20)
		self.upcoming_window.setLayout(layout)

		btn_layout = QHBoxLayout()
		btn_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
		layout.addLayout(btn_layout)

		sidebar_btn = QPushButton("<")
		sidebar_btn.setStyleSheet("""
								QPushButton {
								background-color: transparent;
								border: none;
								padding: 0;
								margin: 0;
								text-align: center;
								color: #a0a0a0;
								}
								QPushButton:hover {
								color: #07C160;
								}
								QPushButton:pressed {
								color: #05974C;
								}
								""")
		set_font(sidebar_btn, 1)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setStyleSheet("""
								 QPushButton {
								background-color: transparent;
								border: none;
								padding: 0;
								margin: 0;
								text-align: center;
								color: #a0a0a0;
								}
								QPushButton:hover {
								color: rgb(235,51,36);
								}
								QPushButton:pressed {
								color: rgb(189,41,29);
								}
								""")
		set_font(return_btn, 1)
		return_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))

		btn_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		btn_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)

		self.upcoming = Upcoming()
		Emitter.instance().view_and_edit_schedule_signal.connect(self.check_one_schedule)
		layout.addWidget(self.upcoming)
		self.add_page(self.main_stack, self.upcoming_window, "Upcoming")

		# 创建悬浮按钮
		float_btn = FloatingButton(self.upcoming_window)
		float_btn.move(50, 50)  # 初始位置
		float_btn.raise_()  # 确保在最上层
		float_btn.clicked.connect(partial(self.navigate_to, "Schedule", self.main_stack))

	def add_page(self, stack: QStackedWidget, widget: QWidget, name: str):
		'''
		向 stack 中添加页面
		'''
		self.main_stack_map[name] = stack.addWidget(widget)

	def navigate_to(self, name: str, stack: QStackedWidget, date: QDate = None, tag: tuple = None):
		'''
		通过名称跳转页面
		'''
		if name in self.main_stack_map:
			# 向Schedule传输date
			if name != "Schedule":
				self.schedule.theme_text_edit.clear()
				self.schedule.text_edit.clear()
				self.id = None
			if name == 'Upcoming':
				self.upcoming.refresh_upcoming()
			elif name == "Schedule":
				if not date is None:
					self.schedule.receive_date(date)
				else:
					self.schedule.deadline_edit.setDateTime(QDateTime.currentDateTime())
					self.schedule.reminder_edit.setDateTime(QDateTime.currentDateTime())
			stack.setCurrentIndex(self.main_stack_map[name])
			log.info(f"跳转到{name}页面，日期为{date.toString() if date else date}")
		else:
			raise RuntimeError(f"错误：未知页面 {name}")

	def check_one_schedule(self, data: tuple):
		event: BaseEvent = data[0]
		self.schedule.id = event.id
		self.schedule.deadline_edit.setDateTime(QDateTime.fromString(event.datetime, "yyyy-MM-dd HH:mm"))
		self.schedule.reminder_edit.setDateTime(QDateTime.fromString(event.advance_time, "yyyy-MM-dd HH:mm"))
		self.schedule.theme_text_edit.setText(event.title)
		self.schedule.text_edit.setPlainText(event.notes)
		self.main_stack.setCurrentIndex(self.main_stack_map["Schedule"])

	# self.schedule.save_btn.clicked.connect(lambda: self.upcoming.delete_one_item(event))

	def setup_search_column_animation(self) -> None:
		"""搜索结果栏展开动画设置"""
		self.animations["search_column"] = QPropertyAnimation(self.search_column, b"maximumWidth")
		self.animations["search_column"].setDuration(300)
		self.animations["search_column"].setEasingCurve(QEasingCurve.Type.InOutQuad)

	def get_search_result(self):
		"""向后端发送搜索内容"""
		text = self.search_edit.text().split()
		if len(text) > 0:
			self.search_column.load_searched_data(tuple(text))
			self.search_edit.clear()

		if not self.search_column_visible:
			self.toggle_search_column()

	def toggle_search_column(self):
		"""处理search_column的变化"""
		self.search_column_visible = not self.search_column_visible

		if self.search_column_visible:
			self.animations["search_column"].setStartValue(0)
			self.animations["search_column"].setEndValue(250)
		else:
			self.animations["search_column"].setStartValue(250)
			self.animations["search_column"].setEndValue(0)

		self.animations["search_column"].start()

	def setup_sidebar_animation(self) -> None:
		"""侧边栏展开动画设置"""
		self.animations["sidebar"] = QPropertyAnimation(self.sidebar, b"maximumWidth")
		self.animations["sidebar"].setDuration(300)
		self.animations["sidebar"].setEasingCurve(QEasingCurve.Type.InOutQuad)

	def toggle_sidebar(self, btn) -> None:
		"""处理sidebar的变化"""
		self.sidebar_visible = not self.sidebar_visible

		if self.sidebar_visible:
			self.animations["sidebar"].setStartValue(0)
			self.animations["sidebar"].setEndValue(230)
			btn.setText("<")
		else:
			self.animations["sidebar"].setStartValue(230)
			self.animations["sidebar"].setEndValue(0)
			btn.setText(">")

		self.animations["sidebar"].start()

	def _init_tray(self):
		"""初始化系统托盘"""
		self.tray = Tray(
			app=QApplication.instance(),
			icon_path=self._get_icon_path()
		)
		# 信号连接：托盘目录(右键显示)
		self.tray.show_main.connect(self.show)
		self.tray.show_floating.connect(self.show_floating_window)
		self.tray.exit_app.connect(self.quit_application)
		self.tray.activated_response.connect(self.show_main_window)
		# 初始化托盘图标提醒
		self.notice_system.notify_to_tray.connect(self.tray.notification_received)

	def _get_icon_path(self):  # 暂时无用
		"""获取图标路径"""
		base_dir = os.path.dirname(__file__)
		return os.path.join(base_dir, "resources", "app_icon.ico")

	def show_floating_window(self):
		"""显示悬浮窗口"""
		if not self.floating_window:
			self.floating_window = FloatingWindow()
		self.floating_window.show()

	def quit_application(self):
		"""退出程序"""
		log.info("quit_application 方法被调用")
		self.tray.shutdown()
		if not self.floating_window is None:
			self.floating_window.close()
		QApplication.quit()

	def closeEvent(self, event):
		"""重写关闭事件"""
		log.info("closeEvent 方法被调用")
		self.hide()
		event.ignore()

	# 最小化按钮重定义为显示悬浮窗
	def changeEvent(self, event):
		# 检查事件类型是否为窗口状态改变事件
		if event.type() == QEvent.WindowStateChange:
			# 检查窗口是否变为最小化状态
			if self.windowState() & Qt.WindowMinimized:
				# 在这里添加窗口最小化时要执行的自定义操作
				print("悬浮窗已经打开")
				# 显示悬浮窗并连接通知信号和主窗口
				self.show_floating_window()
		# 调用父类的 changeEvent 方法以确保默认行为被执行
		super().changeEvent(event)

	# 处理悬浮窗返回主窗口的逻辑
	def show_main_window(self):
		if self.windowState() == Qt.WindowMinimized:
			self.showNormal()
		elif self.isHidden():
			self.show()

	def _init_floating_window(self):
		self.floating_window = FloatingWindow()
		# 连接通知系统
		self.notice_system.notify_to_floating_window.connect(self.floating_window.notification_received)
		# 连接悬浮窗
		self.floating_window.exit_requested.connect(self.quit_application)
		self.floating_window.show_main_requested.connect(self.show_main_window)

	def load_event_in_calendar(self, events: list[DDLEvent]):
		for event in events:
			self.main_window_calendar.add_schedule(event)

	def eventFilter(self, obj, event):
		"""事件过滤器，用于Calendar的search_column"""
		if event.type() == QEvent.MouseButtonPress:
			# 如果当前显示的是带侧边栏的页面
			if self.main_stack.currentWidget() == self.main_window:
				# 处理文本框点击
				if obj == self.search_edit and not self.search_column_visible and event.button() == Qt.LeftButton:
					self.toggle_search_column()  # 打开侧边栏
				# 处理收起侧边栏
				else:
					mouse_pos = event.globalPosition().toPoint()
					search_column_pos = self.search_column.mapFromGlobal(mouse_pos)
					search_edit_pos = self.search_edit.mapFromGlobal(mouse_pos)
					if self.search_column_visible and not self.search_column.rect().contains(
							search_column_pos) and not self.search_edit.rect().contains(search_edit_pos):
						self.toggle_search_column()

		return super().eventFilter(obj, event)

	def get_events_in_month_from_backend(self, cur_year: int, cur_month: int):
		"""获取当前月份的事件"""
		events: list[DDLEvent] = get_events_in_month(cur_year, cur_month)
		self.load_event_in_calendar(events)
