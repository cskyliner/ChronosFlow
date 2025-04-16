from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QDate, Qt
from SideBar import SideBar
from Calendar import Calendar

class MainWindow(QMainWindow):
	def __init__(self, width=800, height=600, show_x=100, show_y=100):
		super().__init__()

		# 尺寸
		self.width = width
		self.height = height
		self.setWindowTitle("todolist")
		self.setGeometry(show_x, show_y, width, height)

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

		# 主窗口
		self.main_window = QWidget()
		# self.main_window.setStyleSheet("background-color: white;")
		main_window_layout = QVBoxLayout()  # 内容区域布局
		main_window_layout.setContentsMargins(20, 5, 20, 20)
		self.main_layout.addWidget(self.main_window)
		self.main_window.setLayout(main_window_layout)

		# 按钮，控制侧边栏显示、隐藏
		self.toggle_btn = QPushButton("<")
		self.toggle_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: white;
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
		self.main_window_calendar.clicked.connect(self.on_date_clicked)
		main_window_layout.addWidget(self.main_window_calendar, alignment=Qt.AlignmentFlag.AlignCenter)

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

	# 日期被左键点击 TODO:点击后续操作
	def on_date_clicked(self, date:QDate) -> None:
		print(date.toString("yyyy年MM月dd日"))
