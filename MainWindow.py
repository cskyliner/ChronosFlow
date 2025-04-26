from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from SideBar import SideBar
from Calendar import Calendar
from functools import partial
from CreateEventWindow import Schedule
from Emitter import Emitter


class MainWindow(QMainWindow):
	def __init__(self, width=800, height=600, show_x=100, show_y=100):
		super().__init__()
		# 尺寸
		self.width = width
		self.height = height
		self.setWindowTitle("todolist")
		self.setGeometry(show_x, show_y, width, height)

		# 信号
		self.emitter = Emitter()

		# 动画管理集
		self.animations = {}

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
		self.setup_animation()

		# 主窗口（设计为堆叠窗口，有多个界面）
		self.main_stack = QStackedWidget()
		self.main_layout.addWidget(self.main_stack)

		# 连接sidebar的信号
		self.sidebar.emitter.page_change_signal.connect(partial(self.navigate_to, stack=self.main_stack, date=None))

		# 通过名称记录页面，使用字典双向映射
		self.main_stack_map = {}  # 名称→索引

		# 设置 main_stack各页面的内容
		self.setup_main_window()  # 日历窗口（主界面）
		self.setup_create_event_window()  # 日程填写窗口
		self.setup_setting_window()
		self.setup_upcoming_window()

	# main_window创建
	def setup_main_window(self):
		self.main_window = QWidget()
		main_window_layout = QVBoxLayout()  # 内容区域布局
		main_window_layout.setContentsMargins(20, 5, 20, 20)
		self.main_window.setLayout(main_window_layout)

		# 按钮，控制侧边栏显示、隐藏
		self.toggle_btn = QPushButton("<")
		self.toggle_btn.setStyleSheet("""
		            QPushButton {
		                padding: 8px;
		                background-color: transparent;
		                border: 1px solid #ccc;
		                border-radius: 4px;
		            }
		            QPushButton:hover {
		                background-color: #e0e0e0;
		            }
		        """)
		self.toggle_btn.clicked.connect(self.toggle_sidebar)
		main_window_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)

		# 创建日历界面
		self.main_window_calendar = Calendar()
		self.main_window_calendar.setGridVisible(False)
		self.main_window_calendar.setFixedSize(int((self.width - 230) * 0.9), int(self.height * 0.8))
		self.main_window_calendar.clicked.connect(
			lambda date: self.navigate_to("Schedule", self.main_stack, date))  # 点击日历时跳转到 schedule
		main_window_layout.addWidget(self.main_window_calendar, alignment=Qt.AlignmentFlag.AlignCenter)

		self.add_page(self.main_stack, self.main_window, "Calendar")  # main_window 是日历，故名为calendar

	# 创建 create_event_window
	def setup_create_event_window(self):
		self.create_event_window = QWidget()
		schedule_layout = QVBoxLayout()  # 内容区域布局
		schedule_layout.setContentsMargins(20, 5, 20, 20)
		self.create_event_window.setLayout(schedule_layout)

		# 返回按钮，回到calendar
		self.schedule_toggle_btn = QPushButton("✕")
		self.schedule_toggle_btn.setStyleSheet("""
				            QPushButton {
				                padding: 8px;
				                background-color: transparent;
				                border: 1px solid #ccc;
				                border-radius: 4px;
				            }
				            QPushButton:hover {
				                background-color: #e0e0e0;
				            }
				        """)
		self.schedule_toggle_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))
		schedule_layout.addWidget(self.schedule_toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)

		# 创建Schedule
		self.schedule = Schedule()
		schedule_layout.addWidget(self.schedule)
		self.add_page(self.main_stack, self.create_event_window, "Schedule")

	# TODO
	def setup_setting_window(self):
		self.setting_window = QWidget()
		self.add_page(self.main_stack, self.setting_window, "Setting")

	# TODO
	def setup_upcoming_window(self):
		self.upcoming_window = QWidget()
		self.add_page(self.main_stack, self.upcoming_window, "Upcoming")

	# 向 stack 中添加页面
	def add_page(self, stack, widget, name):
		self.main_stack_map[name] = stack.addWidget(widget)

	# 通过名称跳转页面
	def navigate_to(self, name, stack, date=None):
		if name in self.main_stack_map:
			# 向Schedule传输date
			if not date is None:
				self.emitter.dynamic_signal.connect(self.schedule.receive_signal)
				self.emitter.send_dynamic_signal(date)

			stack.setCurrentIndex(self.main_stack_map[name])
		else:
			print(f"警告：未知页面 {name}")

	# 侧边栏展开动画设置
	def setup_animation(self) -> None:
		self.animations["sidebar"] = QPropertyAnimation(self.sidebar, b"maximumWidth")
		self.animations["sidebar"].setDuration(300)
		self.animations["sidebar"].setEasingCurve(QEasingCurve.Type.InOutQuad)

	# 处理sidebar的变化
	def toggle_sidebar(self) -> None:
		self.sidebar_visible = not self.sidebar_visible

		if self.sidebar_visible:
			self.animations["sidebar"].setStartValue(0)
			self.animations["sidebar"].setEndValue(230)
			self.toggle_btn.setText("<")
		else:
			self.animations["sidebar"].setStartValue(230)
			self.animations["sidebar"].setEndValue(0)
			self.toggle_btn.setText(">")

		self.animations["sidebar"].start()
