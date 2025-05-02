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
log = logging.getLogger(__name__)
class MainWindow(QMainWindow):
	
	def __init__(self, width=800, height=600, show_x=100, show_y=100):
		super().__init__()
		# 尺寸
		self.width = width
		self.height = height
		self.setWindowTitle("todolist")
		self.setGeometry(show_x, show_y, width, height)

		# 动画管理集
		self.animations:dict[str,QPropertyAnimation] = {}

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
		Emitter.instance().page_change_signal.connect(partial(self.navigate_to, stack=self.main_stack, date=None))

		# 通过名称记录页面，使用字典双向映射
		self.main_stack_map = {}  # 名称→索引

		# 设置 main_stack各页面的内容
		self.setup_main_window()  # 日历窗口（主界面）
		self.setup_create_event_window()  # 日程填写窗口
		self.setup_setting_window()
		self.setup_upcoming_window()

		# 初始化通知系统
		self.notice_system = Notice()

		# 初始化托盘
		self.tray = None
		self._init_tray()
        
        # 悬浮窗口初始化
		self.floating_window = None

		# 临时测试,手动添加了一个日程 (提供接口)
		self.add_schedule()

		# 或许可以有
		# self.setWindowIcon(QIcon(self._get_icon_path()))

	def setup_main_window(self):
		'''
		main_window创建
		'''
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

	def setup_create_event_window(self):
		'''
		创建 create_event_window
		'''
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

	def setup_setting_window(self):
		'''
		TODO:创建设置栏
		'''
		self.setting_window = QWidget()
		setting_layout = QVBoxLayout() # 内容区域布局
		setting_layout.setContentsMargins(20, 5, 20, 20)
		self.setting_window.setLayout(setting_layout)

		# 返回按钮，回到calendar
		self.setting_toggle_btn = QPushButton("X")
		self.setting_toggle_btn.setStyleSheet("""
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
		self.setting_toggle_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))
		setting_layout.addWidget(self.setting_toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)

		self.setting = SettingsPage()
		setting_layout.addWidget(self.setting)
		self.add_page(self.main_stack, self.setting_window, "Setting")


	def setup_upcoming_window(self):
		'''
		TODO:
		'''
		self.upcoming_window = QWidget()
		self.add_page(self.main_stack, self.upcoming_window, "Upcoming")

	def add_page(self, stack:QStackedWidget, widget:QWidget, name:str):
		'''
		向 stack 中添加页面
		'''
		self.main_stack_map[name] = stack.addWidget(widget)

	def navigate_to(self, name:str, stack:QStackedWidget, date:QDate=None):
		'''
		通过名称跳转页面
		'''
		if name in self.main_stack_map:
			# 向Schedule传输date
			if not date is None:
				# Emitter.instance().dynamic_signal.connect(self.schedule.receive_signal)
				# Emitter.instance().send_dynamic_signal(date)
				self.schedule.receive_date(date)
			stack.setCurrentIndex(self.main_stack_map[name])
			log.info(f"跳转到{name}页面，日期为{date.toString() if date else date}")
		else:
			raise RuntimeError(f"错误：未知页面 {name}")

	def setup_animation(self) -> None:
		'''
		侧边栏展开动画设置
		'''
		self.animations["sidebar"] = QPropertyAnimation(self.sidebar, b"maximumWidth")
		self.animations["sidebar"].setDuration(300)
		self.animations["sidebar"].setEasingCurve(QEasingCurve.Type.InOutQuad)

	def toggle_sidebar(self) -> None:
		'''
		处理sidebar的变化
		'''
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
		# 初始化托盘图标提醒
		self.tray.show_notification("启动提醒", "程序已添加到系统托盘")
		self.notice_system.notify_to_tray.connect(self.tray.notification_received)


	def _get_icon_path(self):# 暂时无用
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
		print("quit_application 方法被调用")
		self.tray.shutdown()
		self.floating_window.close()
		QApplication.quit()

	def closeEvent(self, event):
		"""重写关闭事件"""
		print("closeEvent 方法被调用")
		event.accept()

	def add_schedule(self, title = "会议提醒", content = "10分钟后有项目进度会议", 
				  notify_time = QDateTime.currentDateTime().addSecs(5)
				  , color="#3498db"):
        # 示例：添加一个5秒后的通知
		self.notice_system.schedule_notice(
            title,
           	content,
            notify_time,
            color # 绿色通知
        )
		# 用于在通知时自动显示悬浮窗
		self.notice_system.notify_show_floating_window.connect(self.show_floating_window_and_connect)
		
	# 最小化按钮重定义为显示悬浮窗
	def changeEvent(self, event):
		# 检查事件类型是否为窗口状态改变事件
		if event.type() == QEvent.WindowStateChange:
			# 检查窗口是否变为最小化状态
			if self.windowState() & Qt.WindowMinimized:
				# 在这里添加窗口最小化时要执行的自定义操作
				print("悬浮窗已经打开")
				# 显示悬浮窗并连接通知信号和主窗口
				self.show_floating_window_and_connect()
		# 调用父类的 changeEvent 方法以确保默认行为被执行
		super().changeEvent(event)

	#处理悬浮窗返回主窗口的逻辑
	def show_main_window(self):
		if self.windowState() == Qt.WindowMinimized:
			print("目前最小化")
			self.showNormal()
		elif self.isHidden():
			print("目前隐藏")
			self.show()

	#打包操作
	def show_floating_window_and_connect(self):
		# 显示悬浮窗
		self.show_floating_window()
		# 连接通知系统
		self.notice_system.notify_to_floating_window.connect(self.floating_window.notification_received)
		# 连接悬浮窗
		self.floating_window.exit_requested.connect(self.quit_application)
		self.floating_window.show_main_requested.connect(self.show_main_window)