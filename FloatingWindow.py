from common import *
# ---------------------- 悬浮窗口类 ----------------------
from Notice import NotificationWidget
from Event import DDLEvent

class FloatingWindow(QWidget):
	exit_requested = Signal()  # 完全退出信号
	show_main_requested = Signal()  # 显示主窗口信号
	notification_received = Signal(object)  # 通知信号

	def __init__(self, parent=None, show_x=40, show_y=400, width=300, height=200):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
		# self.setFixedSize(600, 400)
		self.notification_widgets = []
		self._init_ui()
		self._connect_signals()
		self.setGeometry(show_x, show_y, width, height)
		self.draggable = False
		self.offset = None

	def _init_ui(self):
		# 主布局
		main_layout = QVBoxLayout()
		main_layout.setContentsMargins(15, 15, 15, 15)
		main_layout.setSpacing(15)

		# 标题栏
		header = QHBoxLayout()
		self.title_label = QLabel("快捷控制面板")
		self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
		header.addWidget(self.title_label)

		# 隐藏按钮
		self.btn_hide = QPushButton("×")
		self.btn_hide.setFixedSize(24, 24)
		self.btn_hide.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border-radius: 12px;
                font-size: 16px;
            }
            QPushButton:hover { background: #c0392b; }
        """)
		self.btn_hide.clicked.connect(self.hide)
		header.addWidget(self.btn_hide)

		main_layout.addLayout(header)

		# 控制按钮
		control_layout = QVBoxLayout()
		control_layout.setSpacing(12)

		# 返回主界面按钮
		self.btn_main = QPushButton("返回主界面")
		self.btn_main.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #2980b9; }
        """)
		control_layout.addWidget(self.btn_main)

		# 退出程序按钮
		self.btn_exit = QPushButton("退出")
		self.btn_exit.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #c0392b; }
        """)
		control_layout.addWidget(self.btn_exit)

		main_layout.addLayout(control_layout)

		# 通知区域
		self.notification_area = QVBoxLayout()
		self.notification_area.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
		main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
		main_layout.addLayout(self.notification_area)

		self.setLayout(main_layout)

		# 窗口样式
		self.setStyleSheet("""
            FloatingWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f5f7fa, stop:1 #c3cfe2
                );
                border-radius: 12px;
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
		event = data[0]
		notification = NotificationWidget(event.title, event.notes, "#3498db", self)
		self.notification_area.addWidget(notification)
		notification.show()
		self.notification_widgets.append(notification)

		# 自动排列通知
		# self._arrange_notifications()

	def _arrange_notifications(self):  # 暂时无用
		"""排列通知位置"""
		y_pos = self.height() - 50
		for widget in self.notification_widgets:
			if widget.isVisible():
				widget.move(self.width() - widget.width() - 20, y_pos)
				y_pos -= widget.height() + 10

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
			print(self.pos())

	def closeEvent(self, event):
		# 确保资源释放和状态更新
		self.notification_widgets = []
		# 移除窗口置顶标志
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
		self.update()
		# 延迟 0.1 秒
		time.sleep(0.1)
		event.accept()
