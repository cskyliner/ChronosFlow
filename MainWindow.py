from common import *
from SideBar import SideBar
from NewCalendar import CalendarView
from functools import partial
from CreateEventWindow import Schedule
from Emitter import Emitter
from Settings import SettingsPage
from Tray import Tray
from FloatingWindow import FloatingWindow
from Notice import Notice
from Upcoming import Upcoming, FloatingButton
from Weekview import WeekView
from Weekview import WeekView
from FontSetting import set_font
from HeatMap import YearHeatMapView
from events.Event import *
from events.EventManager import EventSQLManager
import re
log = logging.getLogger(__name__)


class MainWindow(QMainWindow):

	def __init__(self, app, width=1000, height=600):
		super().__init__()
		self.setWindowTitle("ChronosFlow")
		# self.main_window_calendar = None

		# === App 菜单栏（仅 macOS 显示）===
		if sys.platform == "darwin":
			menubar = self.menuBar()
			app_menu = menubar.addMenu("ChronosFlow")

			about_action = QAction("About ChronosFlow", self)
			about_action.triggered.connect(self.show_about_dialog)
			app_menu.addAction(about_action)

			quit_action = QAction("Quit", self)
			quit_action.triggered.connect(app.quit)
			app_menu.addAction(quit_action)

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
		self.main_layout.addWidget(self.main_stack)

		# 连接sidebar的信号
		Emitter.instance().page_change_signal.connect(partial(self.navigate_to, stack=self.main_stack, date=None))
		# 通过名称记录页面，使用字典双向映射
		self.main_stack_map = {}  # 名称→索引

		# 设置 main_stack各页面的内容，注意初始化顺序
		self.setup_setting_window()  # 设置界面
		self.setup_main_window()  # 日历窗口（主界面）
		self.setup_create_event_window()  # 日程填写窗口
		self.setup_upcoming_window()  # 日程展示窗口
		self.setup_week_view_window() # 周视图窗口
		self.setup_heatmap_window() # 热力图窗口
		Emitter.instance().delete_activity_event_signal.connect(self.week_view.update_view_geometry)
		self.navigate_to("Calendar", self.main_stack)
		# 初始化通知系统
		self.notice_system = Notice()
		# 用于在通知时自动显示悬浮窗
		self.notice_system.notify_show_floating_window.connect(self.show_floating_window)

		# 初始化托盘
		self.tray = None
		self._init_tray()

		# 悬浮窗口初始化
		self._init_floating_window()

		# 设置壁纸
		self.set_wallpaper(self.setting.wallpaper_path)

		# 安装事件过滤器，处理Calendar页面的侧边栏的收放
		self.main_stack.installEventFilter(self)
		self.search_column.installEventFilter(self)
		self.search_edit.installEventFilter(self)

	# 或许可以有
	# self.setWindowIcon(QIcon(self._get_icon_path()))
	# === App 菜单栏（仅 macOS 显示）===
	def show_about_dialog(self):
		QMessageBox.about(self, "About ChronosFlow", "This is ChronosFlow.\nA beautiful task planner.")

	def setup_main_window(self):
		"""
		main_window创建，即主日历窗口
		"""
		self.main_window = QWidget()
		main_window_layout = QVBoxLayout()  # 内容区域布局
		main_window_layout.setSpacing(5)  # 设置相邻控件间距为0
		main_window_layout.setContentsMargins(20, 5, 20, 20)
		self.main_window.setLayout(main_window_layout)

		upper_layout = QHBoxLayout()
		upper_layout.setSpacing(0)
		# 添加'<'按钮
		sidebar_btn = QPushButton("")
		sidebar_btn.setFixedSize(35, 30)
		sidebar_btn.setIcon(QIcon("pic/sidebar1.png"))
		sidebar_btn.setIconSize(QSize(24, 24))
		sidebar_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                    background-color: palette(midlight);
				                }
				                QPushButton:pressed {
									background-color: palette(mid);
								}
				            """)
		set_font(sidebar_btn, 4)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 添加上方search文本框
		self.search_edit = QLineEdit()
		self.search_edit.setPlaceholderText("搜索")
		set_font(self.search_edit)
		self.search_edit.setStyleSheet("""
								    QLineEdit {
								    background: transparent;
						            padding: 8px;
					                border: 1px solid #1E90FF;
					                border-top-left-radius: 19px;     /* 左上角 */
    								border-top-right-radius: 0px;    /* 右上角 */
    								border-bottom-left-radius: 19px;  /* 左下角 */
    								border-bottom-right-radius: 0px; /* 右下角 */
    								border-right: none;
					                font-size: 14px;
						            }
							    """)
		self.search_edit.setMinimumWidth(150)
		self.search_edit.setFixedHeight(38)
		# 回车触发搜索功能
		self.search_edit.returnPressed.connect(self.get_search_result)

		# 右侧搜索按钮
		btn = QPushButton()
		btn.setIcon(QIcon.fromTheme("system-search"))
		btn.setStyleSheet("""
					QPushButton {
		                background: transparent;
		                border: 1px solid #1E90FF;
		                border-top-left-radius: 0px;     /* 左上角 */
    					border-top-right-radius: 19px;    /* 右上角 */
    					border-bottom-left-radius: 0px;  /* 左下角 */
    					border-bottom-right-radius: 19px; /* 右下角 */
		                padding: 25px;
		                text-align: center;
		            }
		            QPushButton:hover {
		                border-color: #24C1FF;
		            }
		            QPushButton:pressed {
						border-color: #42BCFF;
					}
				""")
		btn.setFixedSize(38, 38)
		btn.clicked.connect(self.get_search_result)

		upper_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		
		#将上方按钮统一布局后加入主布局
		upper_layout.addStretch(3)
		upper_layout.addWidget(self.search_edit,stretch= 1)
		upper_layout.addWidget(btn,stretch= 1)
		main_window_layout.addLayout(upper_layout)

		middle_layout = QHBoxLayout()
		# 创建日历界面
		self.main_window_calendar = CalendarView()
		self.main_window_calendar.double_clicked.connect(
			lambda date: self.navigate_to("Upcoming", self.main_stack, date))
		self.main_window_calendar.view_single_day.connect(
			lambda date: self.navigate_to("Upcoming", self.main_stack, date))
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
		float_btn.move(50, 50)  										# 初始位置
		float_btn.raise_()  											# 确保在最上层
		float_btn.clicked.connect(partial(self.navigate_to, "Schedule", self.main_stack))

		self.add_page(self.main_stack, self.main_window, "Calendar")  	# main_window是日历，故名为Calendar

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

		sidebar_btn = QPushButton("")
		sidebar_btn.setFixedSize(35, 30)
		sidebar_btn.setIcon(QIcon("pic/sidebar1.png"))
		sidebar_btn.setIconSize(QSize(24, 24))
		sidebar_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                    background-color: palette(midlight);
				                }
				                QPushButton:pressed {
									background-color: palette(mid);
								}
				            """)
		set_font(sidebar_btn, 4)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setFixedSize(35, 30)
		return_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                	color: #E61B23;
				                }
				                QPushButton:pressed {
									color: #B8281C;
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

	def setup_week_view_window(self):
		"""创建周视图窗口"""
		self.week_view_window = QWidget()
		week_view_layout = QVBoxLayout()  # 内容区域布局
		week_view_layout.setSpacing(0)
		week_view_layout.setContentsMargins(20, 5, 20, 20)
		self.week_view_window.setLayout(week_view_layout)

		# 顶部按钮布局
		btn_layout = QHBoxLayout()
		btn_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
		week_view_layout.addLayout(btn_layout)

		# 侧边栏切换按钮
		sidebar_btn = QPushButton("")
		sidebar_btn.setFixedSize(35, 30)
		sidebar_btn.setIcon(QIcon("pic/sidebar1.png"))
		sidebar_btn.setIconSize(QSize(24, 24))
		sidebar_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                    background-color: palette(midlight);
				                }
				                QPushButton:pressed {
									background-color: palette(mid);
								}
				            """)
		set_font(sidebar_btn, 4)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setFixedSize(35, 30)
		return_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                	color: #E61B23;
				                }
				                QPushButton:pressed {
									color: #B8281C;
								}
				            """)
		set_font(return_btn, 1)
		return_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))

		btn_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		btn_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)

		# 添加周视图内容
		self.week_view = WeekView()
		week_view_layout.addWidget(self.week_view)
		self.week_view.floating_button = FloatingButton(self.week_view_window)
		self.week_view.floating_button.move(50, 50)  # 初始位置
		self.week_view.floating_button.raise_()  # 确保在最上层
		self.week_view.floating_button.clicked.connect(partial(self.navigate_to, "Schedule", self.main_stack))		
		self.add_page(self.main_stack, self.week_view_window, "Weekview")
		self.week_view.schedule_area_clicked.connect(lambda info: self.navigate_to("Schedule", self.main_stack, None, ("from_weekview_add",info)))
		self.week_view.schedule_del_btn_clicked.connect(lambda event: Emitter.instance().send_delete_event_signal(event.id, event.table_name()))
		self.week_view.schedule_double_clicked.connect(lambda event: self.check_one_schedule((event,)))

	def setup_heatmap_window(self):
		self.heatmap_window = QWidget()
		# 内容区域布局
		heatmap_layout = QVBoxLayout()
		heatmap_layout.setSpacing(0)
		heatmap_layout.setContentsMargins(20, 5, 20, 20)
		self.heatmap_window.setLayout(heatmap_layout)

		# 顶部按钮布局
		btn_layout = QHBoxLayout()
		btn_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
		heatmap_layout.addLayout(btn_layout)

		# 侧边栏切换按钮
		sidebar_btn = QPushButton("")
		sidebar_btn.setFixedSize(35, 30)
		sidebar_btn.setIcon(QIcon("pic/sidebar1.png"))
		sidebar_btn.setIconSize(QSize(24, 24))
		sidebar_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                    background-color: palette(midlight);
				                }
				                QPushButton:pressed {
									background-color: palette(mid);
								}
				            """)
		set_font(sidebar_btn, 4)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setFixedSize(35, 30)
		return_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                	color: #E61B23;
				                }
				                QPushButton:pressed {
									color: #B8281C;
								}
				            """)
		set_font(return_btn, 1)
		return_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))

		btn_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		btn_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)
		# 加入热力图
		self.heatmap_view = YearHeatMapView(year=2025)	# 这里年份暂时这样处理
		heatmap_layout.addWidget(self.heatmap_view)
		self.add_page(self.main_stack, self.heatmap_window, "HeatMap")

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

		sidebar_btn = QPushButton("")
		sidebar_btn.setFixedSize(35, 30)
		sidebar_btn.setIcon(QIcon("pic/sidebar1.png"))
		sidebar_btn.setIconSize(QSize(24, 24))
		sidebar_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                    background-color: palette(midlight);
				                }
				                QPushButton:pressed {
									background-color: palette(mid);
								}
				            """)
		set_font(sidebar_btn, 4)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setFixedSize(35, 30)
		return_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                	color: #E61B23;
				                }
				                QPushButton:pressed {
									color: #B8281C;
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

		sidebar_btn = QPushButton("")
		sidebar_btn.setFixedSize(35, 30)
		sidebar_btn.setIcon(QIcon("pic/sidebar1.png"))
		sidebar_btn.setIconSize(QSize(24, 24))
		sidebar_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: none;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                    background-color: palette(midlight);
				                }
				                QPushButton:pressed {
									background-color: palette(mid);
								}
				            """)
		set_font(sidebar_btn, 4)
		sidebar_btn.clicked.connect(partial(self.toggle_sidebar, btn=sidebar_btn))

		# 返回按钮，回到calendar
		return_btn = QPushButton("✕")
		return_btn.setFixedSize(35, 30)
		return_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border-radius: 5px;
				                    padding: 5;
		    						margin: 0;
				                    text-align: center;
				                    color: palette(text);
				                }
				                QPushButton:hover {
				                	color: #E61B23;
				                }
				                QPushButton:pressed {
									color: #B8281C;
								}
				            """)
		set_font(return_btn, 1)
		return_btn.clicked.connect(partial(self.navigate_to, "Calendar", self.main_stack))

		btn_layout.addWidget(sidebar_btn, alignment=Qt.AlignmentFlag.AlignLeft)
		btn_layout.addWidget(return_btn, alignment=Qt.AlignmentFlag.AlignRight)

		self.upcoming = Upcoming(0)
		Emitter.instance().view_and_edit_schedule_signal.connect(self.check_one_schedule)
		layout.addWidget(self.upcoming)
		self.add_page(self.main_stack, self.upcoming_window, "Upcoming")

		# 创建悬浮按钮
		self.upcoming.float_btn = FloatingButton(self.upcoming_window)
		self.upcoming.float_btn.move(50, 50)  # 初始位置
		self.upcoming.float_btn.raise_()  # 确保在最上层
		self.upcoming.float_btn.clicked.connect(partial(self.navigate_to, "Schedule", self.main_stack))
		#self.upcoming.del_activity_event_signal.connect(self.week_view.update_view_geometry)


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
				self.schedule.refresh()
			if name == 'Upcoming':
				self.upcoming.float_btn.clicked.disconnect()
				if date is not None:
					self.upcoming.show_specific_date(date)
					self.upcoming.float_btn.clicked.connect(
						partial(self.navigate_to, "Schedule", self.main_stack, date))
				else:
					self.upcoming.refresh_upcoming()
					self.upcoming.float_btn.clicked.connect(partial(self.navigate_to, "Schedule", self.main_stack))
			elif name == "Schedule":
				self.schedule.group_box.setTitle("添加DDL")
				if not date is None:
					self.schedule.receive_date(date)
				elif tag is not None:
					info = tag[0]
					if info == "from_weekview_add":
						bg_t:QTime = tag[1][0]
						en_t:QTime = tag[1][1]
						date:QDate = tag[1][2]
						self.schedule.type_choose_combo.setCurrentText("日程")
						self.schedule.type_choose_combo.setEnabled(True)      
						self.schedule.start_date_edit.setDate(date)
						self.schedule.end_date_edit.setDate(date)
						self.schedule.start_time_edit.setTime(bg_t)
						self.schedule.end_time_edit.setTime(en_t)	
							
				else:
					self.schedule.deadline_date_edit.setDate(QDate.currentDate())
					self.schedule.deadline_time_edit.setTime(QTime.currentTime())
					self.schedule.reminder_date_edit.setDate(QDate.currentDate())
					self.schedule.reminder_time_edit.setTime(QTime.currentTime())
			elif name == "Calendar":
				self.main_window_calendar.refresh()
			elif name == "Weekview":
				self.week_view.load_schedules()
			elif name == "HeatMap":
				self.heatmap_view.refresh(year=2025)
			stack.setCurrentIndex(self.main_stack_map[name])
			log.info(f"跳转到{name}页面，日期为{date.toString() if date else date}")
		else:
			raise RuntimeError(f"错误：未知页面 {name}")

	def check_one_schedule(self, data: tuple):
		event: BaseEvent = data[0]
		if isinstance(event, DDLEvent):
			self.schedule.id = event.id
			datetime = QDateTime.fromString(event.datetime, "yyyy-MM-dd HH:mm")
			remainder_datetime = QDateTime.fromString(event.advance_time, "yyyy-MM-dd HH:mm")
			self.schedule.deadline_date_edit.setDate(datetime.date())
			self.schedule.deadline_time_edit.setTime(datetime.time())
			self.schedule.reminder_date_edit.setDate(remainder_datetime.date())
			self.schedule.reminder_time_edit.setTime(remainder_datetime.time())
			self.schedule.theme_text_edit.setText(event.title)
			self.schedule.text_edit.setPlainText(event.notes)
			self.schedule.group_box.setTitle("编辑DDL")
			self.schedule.type_choose_combo.setCurrentText("DDL")
			self.schedule.type_choose_combo.setEnabled(False)
		elif isinstance(event,ActivityEvent):
			# 编辑日程时候对于事件的恢复
			self.schedule.id = event.id
			self.schedule.start_date_edit.setDate(QDate.fromString(event.start_date, "yyyy-MM-dd"))
			self.schedule.start_time_edit.setTime(QTime.fromString(event.start_time, "HH:mm"))
			self.schedule.end_date_edit.setDate(QDate.fromString(event.end_date, "yyyy-MM-dd"))
			self.schedule.end_time_edit.setTime(QTime.fromString(event.end_time, "HH:mm"))
			self.schedule.repeat_combo.setCurrentText(event.repeat_type)
			if event.repeat_type != '不重复':
				english_to_chinese = {'Mon': '周一', 'Tue': '周二', 'Wed': '周三', 'Thu': '周四', 'Fri': '周五',
									'Sat': '周六', 'Sun': '周日'}
				weekdays = json.loads(event.repeat_days)
				# 这里暂时只能选一周内的一天
				self.schedule.repeat_day_combo.setCurrentText(english_to_chinese[weekdays[0]])
			self.schedule.group_box.setTitle("编辑日程")
			self.schedule.type_choose_combo.setCurrentText("日程")
			self.schedule.type_choose_combo.setEnabled(False)
			bg_t:QTime = QTime.fromString(event.start_time,"HH:mm")
			en_t:QTime = QTime.fromString(event.end_time,"HH:mm")
			st_date:QDate = QDate.fromString(event.start_date, "yyyy-MM-dd")
			en_date:QDate = QDate.fromString(event.end_date, "yyyy-MM-dd")
			self.schedule.type_choose_combo.setCurrentText("日程")
			self.schedule.theme_text_edit.setText(event.title)
			self.schedule.text_edit.setPlainText(event.notes)
			self.schedule.type_choose_combo.setEnabled(True)      
			self.schedule.start_date_edit.setDate(st_date)
			self.schedule.end_date_edit.setDate(en_date)
			self.schedule.start_time_edit.setTime(bg_t)
			self.schedule.end_time_edit.setTime(en_t)

		self.main_stack.setCurrentIndex(self.main_stack_map["Schedule"])

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
			btn.setIcon(QIcon("pic/sidebar1.png"))
			btn.setIconSize(QSize(24, 24))
			btn.setText("")
		else:
			self.animations["sidebar"].setStartValue(230)
			self.animations["sidebar"].setEndValue(0)
			btn.setIcon(QIcon("pic/sidebar2.png"))
			btn.setIconSize(QSize(24, 24))
			btn.setText("")

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
		events: list[DDLEvent] = EventSQLManager.get_events_in_month(cur_year, cur_month)
		self.main_window_calendar.schedules.clear()
		self.load_event_in_calendar(events)

	def is_valid_wallpaper(self, path: str) -> bool:
		"""检查壁纸路径是否有效"""
		# 1. 检查路径是否为空
		if not path or path.strip() == "" or path == "无壁纸":
			return False

		# 2. 检查文件是否存在且可读
		if not QFile(path).exists() or not QFile(path).permissions() & QFile.ReadUser:
			return False

		# 3. 检查文件格式是否被支持
		supported_formats = QImageReader.supportedImageFormats()
		file_suffix = QFileInfo(path).suffix().lower()
		if file_suffix.encode() not in supported_formats:
			return False

		# 检查 Windows 下的合法路径格式
		if sys.platform == "win32" and not re.match(r"^[a-zA-Z]:", path):
			return False

		# 检查 macOS 是否具有访问权限（沙盒环境下需要额外授权）
		if sys.platform == "darwin" and not path.startswith("/Users/"):
			log.error("警告：非用户目录可能无权限访问该壁纸路径")
			return False

		return True

	def set_wallpaper(self, path: str):
		"""安全设置壁纸背景"""
		if self.is_valid_wallpaper(path):
			# 处理路径格式
			if " " in path:
				path = f'"{path}"'  # 空格路径添加引号

			# 更新样式表
			self.main_stack.setStyleSheet(f"""
				            QStackedWidget {{
				                background-image: url({path});
				                background-position: center;
				                background-repeat: no-repeat;
				                background-size: contain;
				            }}
				        """)
		else:
			log.error("警告：壁纸路径无效")
