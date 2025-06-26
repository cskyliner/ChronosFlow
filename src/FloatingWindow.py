from common import *
from Notice import NotificationWidget
from events.Event import *

log = logging.getLogger(__name__)

class FloatingWindow(QWidget):
	exit_requested = Signal()  # 完全退出信号
	show_main_requested = Signal()  # 显示主窗口信号
	notification_received = Signal(object)  # 通知信号

	def __init__(self, parent=None, show_x=40, show_y=532, width=150, height=160):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
		self.setFixedSize(150, 160)
		self.notification_widgets = []
		self.lattest_event = None
		self._init_ui()
		self._connect_signals()
		self.setGeometry(show_x, show_y, width, height)
		self.draggable = False
		self.offset = None

	def _init_ui(self):
		# 主布局
		main_layout = QVBoxLayout()
		main_layout.setContentsMargins(8, 8, 8, 8)
		main_layout.setSpacing(5)

		# 标题栏
		header = QHBoxLayout()
		#header.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.title_label = QLabel("快捷控制面板")
		self.title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #2c3e50;")#原来16
		header.addWidget(self.title_label)

		# 隐藏按钮
		self.btn_hide = QPushButton("×")
		self.btn_hide.setFixedSize(16, 16)
		self.btn_hide.setStyleSheet("""
			QPushButton {
				background: #e74c3c;
				color: white;
				border-radius: 6px;
				font-size: 14px;
			}
			QPushButton:hover { background: #c0392b; }
		""")
		#原来参数3,4行:10,16
		self.btn_hide.clicked.connect(self.hide)
		#header.setAlignment(Qt.AlignmentFlag.AlignRight)
		header.addWidget(self.btn_hide)

		main_layout.addLayout(header)

		# 控制按钮
		control_layout = QVBoxLayout()
		control_layout.setSpacing(7)#12

		# 返回主界面按钮
		self.btn_main = QPushButton("返回主界面")
		self.btn_main.setStyleSheet("""
			QPushButton {
				background: #3498db;
				color: white;
				padding: 4px;
				border-radius: 3px;
				font-size: 12px;
			}
			QPushButton:hover { background: #2980b9; }
		""")
		
		"""                padding: 8px;
				border-radius: 6px;
		"""
		control_layout.addWidget(self.btn_main)

		# 退出程序按钮
		self.btn_exit = QPushButton("退出")
		self.btn_exit.setStyleSheet("""
			QPushButton {
				background: #e74c3c;
				color: white;
				padding: 4px;
				border-radius: 3px;
				font-size: 12px;
			}
			QPushButton:hover { background: #c0392b; }
		""")
		control_layout.addWidget(self.btn_exit)

		main_layout.addLayout(control_layout)

		# 通知区域
		self.notification_area = QVBoxLayout()
		#self.notification_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
		#main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
		#self.notification_area.addWidget()
		main_layout.addLayout(self.notification_area)

		self.setLayout(main_layout)

		# 窗口样式
		self.setStyleSheet("""
			FloatingWindow {
				background: qlineargradient(
					x1:0, y1:0, x2:1, y2:1,
					stop:0 #f5f7fa, stop:1 #c3cfe2
				);
				border-radius: 7px;
				border: 1px solid #dfe4ea;
			}
		""")

	def _connect_signals(self):
		"""连接信号与槽"""
		self.btn_main.clicked.connect(self.show_main_requested.emit)
		self.btn_exit.clicked.connect(self.exit_requested.emit)
		self.notification_received.connect(self.show_notification)

	@Slot(object)
	def show_notification(self, data:tuple):
		"""显示通知"""

		if(data[0] is None):
			log.info("暂无通知")
		else:	
			log.info(f"收到通知：{data[0].title}")
		self.lattest_event = data[0]
		if self.notification_area.count():#更新时清楚旧通知
			self.notification_area.takeAt(0).widget().setParent(None)
		notification = CountdownLabel(self.lattest_event)
		self.notification_area.addWidget(notification)
		notification.show()

	def paintEvent(self, event):
		"""绘制背景渐变"""
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)

		gradient = QLinearGradient(0, 0, self.width(), self.height())
		gradient.setColorAt(0, QColor(245, 247, 250))
		gradient.setColorAt(1, QColor(195, 207, 226))

		painter.setBrush(gradient)
		painter.setPen(Qt.NoPen)
		painter.drawRoundedRect(self.rect(), 12, 12)

	# 以下三个函数实现鼠标拖动操作：
	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.draggable = True
			self.offset = event.pos()

	def mouseMoveEvent(self, event):
		if self.draggable:
			self.move(self.pos() + event.pos() - self.offset)

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.draggable = False
			#print(self.pos())

	def closeEvent(self, event):
		# 确保资源释放和状态更新
		self.notification_widgets = []
		# 移除窗口置顶标志
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
		self.update()
		# 延迟 0.1 秒
		time.sleep(0.1)
		event.accept()

class CountdownLabel(QLabel):
	def __init__(self, event: DDLEvent, parent=None):
		super().__init__(parent)

		if event is None: 
			self.setText("        DDL event:无")
			return

		self._event = event
		self.end_time = QDateTime.fromString(event.datetime, "yyyy-MM-dd HH:mm")
		self.notify_time = QDateTime.fromString(event.advance_time, "yyyy-MM-dd HH:mm")
		self.setAlignment(Qt.AlignCenter)
		self.setStyleSheet("font-size: 12px; color: #e74c3c;")
		
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_countdown)
		self.timer.start(1000)  # 更新间隔：每秒
		
		self.update_countdown()  # 初次设置

	def update_countdown(self):
		self.setWordWrap(True)
		remaining_end_seconds = QDateTime.currentDateTime().secsTo(self.end_time)
		remaining_notify_seconds = QDateTime.currentDateTime().secsTo(self.notify_time)
		if remaining_notify_seconds <= 0 and remaining_end_seconds > 0:
			end_hours = remaining_end_seconds // 3600
			end_minutes = (remaining_end_seconds % 3600) // 60
			end_seconds = remaining_end_seconds % 60          
			self.setText(f"DDL event:{self._event.title}\n 00:00:00 已提醒\n 距离截止时间:{end_hours:02}:{end_minutes:02}:{end_seconds:02}")
		elif remaining_notify_seconds <= 0 and remaining_end_seconds <= 0:
			self.setText(f"DDL event:{self._event.title}\n 00:00:00 已截止")
			self.timer.stop()
		else:
			end_hours = remaining_end_seconds // 3600
			end_minutes = (remaining_end_seconds % 3600) // 60
			end_seconds = remaining_end_seconds % 60
			notify_hours = remaining_notify_seconds // 3600
			notify_minutes = (remaining_notify_seconds % 3600) // 60
			notify_seconds = remaining_notify_seconds % 60
			self.setText(f"DDL event:{self._event.title}\n 距离提醒时间:{notify_hours:02}:{notify_minutes:02}:{notify_seconds:02}\n 距离截止时间:{end_hours:02}:{end_minutes:02}:{end_seconds:02}")
