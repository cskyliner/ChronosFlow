from common import *
from Event import DDLEvent
if sys.platform == 'darwin':
	import pync
log = logging.getLogger(__name__)
from Emitter import Emitter

class Notice(QObject):
	notify_to_floating_window = Signal(str, str, str)  # 向悬浮窗发送通知信号(标题，内容，颜色代码)
	notify_to_tray = Signal(str, str, str)  # 向托盘发送通知信号(标题，内容，颜色代码)
	notify_show_floating_window = Signal()
	notify_to_backend = Signal()

	def __init__(self):
		super().__init__()
		self.scheduled_notices = []  # 存储计划通知
		self.latest_event:DDLEvent = None
		self.timer = QTimer()
		#self.timer.timeout.connect(self.check_notices)
		self.timer.timeout.connect(self.check_notice)
		self.timer.start(200)  # 每秒检查一次
		Emitter.instance().notice_signal.connect(self.update_latest_event)

	def schedule_notice(self, title, content, notify_time, color="#3498db"):
		"""
		添加计划通知
		:param title: 主题
		:param content: 内容
		:param notify_time: notify_time=QDateTime.currentDateTime().addSecs(5) TODO:notify_time应只为时间
		:param color:颜色
		"""
		self.scheduled_notices.append({
			"title": title,
			"content": content,
			"time": notify_time,
			"color": color
		})
		# 按时间对通知列表进行排序，确保先到期的通知先处理
		self.scheduled_notices.sort(key=lambda x: x["time"])
	def check_notice(self):
		current = QDateTime.currentDateTime()
		if self.latest_event:
			notify_time = QDateTime.fromString(self.latest_event.datetime, "yyyy-MM-dd HH:mm")
			if current >= notify_time:
				log.info(f"提醒: {self.latest_event.title} - {self.latest_event.notes}")
				if sys.platform == "darwin":
					pync.notify(self.latest_event.notes, title='ChronosFlow', subtitle=self.latest_event.title, sound='Ping')
				else:
					self.notify_show_floating_window.emit()
					self.notify_to_floating_window.emit(
						self.latest_event.title,
						self.latest_event.notes,
						"#3498db"
					)
				self.notify_to_tray.emit(
					self.latest_event.title,
					self.latest_event.notes,
					"#3498db"
				)
				self.request_latest_event(current)
	def check_notices(self):
		"""检查是否到达通知时间"""
		current = QDateTime.currentDateTime()
		# 只处理已到期的通知
		while self.scheduled_notices and current >= self.scheduled_notices[0]["time"]:
			notice = self.scheduled_notices.pop(0)
			log.info(f"提醒: {notice['title']} - {notice['content']}")
			if sys.platform == "darwin":
				pync.notify(notice["content"], title='ChronosFlow', subtitle=notice["title"], sound='Ping')
			else:
				self.notify_show_floating_window.emit()
				self.notify_to_floating_window.emit(
					notice["title"],
					notice["content"],
					notice["color"]
				)
			self.notify_to_tray.emit(
				notice["title"],
				notice["content"],
				notice["color"]
			)
	def update_latest_event(self, latest_event:DDLEvent):
		self.latest_event = latest_event
	def request_latest_event(self, cur_time: QDateTime):
		Emitter.instance().request_latest_event_signal(cur_time)


class NotificationWidget(QFrame):
	def __init__(self, title, content, color, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
		self.setFixedSize(250, 100)
		self._init_ui(title, content, color)
		self._start_close_timer()

	def _init_ui(self, title, content, color):
		self.setStyleSheet(f"""
            NotificationWidget {{
                background: {color}15;
                border-radius: 8px;
                border: 2px solid {color};
            }}
        """)

		layout = QVBoxLayout()
		layout.setContentsMargins(12, 8, 12, 8)

		# 标题
		title_label = QLabel(title)
		title_label.setStyleSheet(f"""
            font-size: 14px; 
            font-weight: bold; 
            color: {color};
            margin-bottom: 4px;
        """)
		layout.addWidget(title_label)

		# 内容
		content_label = QLabel(content)
		content_label.setStyleSheet("""
            font-size: 12px;
            color: #2c3e50;
        """)
		layout.addWidget(content_label)

		self.setLayout(layout)

	def _start_close_timer(self):
		"""8秒后自动关闭"""
		QTimer.singleShot(8000, self.close)
