import sys
import os
from src.common import *
from src.events.Event import *

if sys.platform == 'darwin':
    def get_pync():
        import pync
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        pync.TERMINAL_NOTIFIER = os.path.join(base_path, "assets", "terminal-notifier")
        return pync
log = logging.getLogger(__name__)
from src.Emitter import Emitter

def resource_path(relative_path):
	"""兼容 PyInstaller 打包与调试模式"""
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.abspath(relative_path)

class Notice(QObject):
	notify_to_floating_window = Signal(object)  # 向悬浮窗发送通知信号(标题，内容，颜色代码)
	notify_to_tray = Signal(object)  # 向托盘发送通知信号(标题，内容，颜色代码)
	notify_show_floating_window = Signal()
	notify_to_backend = Signal()

	def __init__(self):
		super().__init__()
		self.scheduled_notices = []  # 存储计划通知
		self.if_backend_exist_event = True
		self.latest_event: DDLEvent = None
		self.timer = QTimer()
		self.timer.timeout.connect(self.check_notice)
		self.timer.start(1000)  # 每秒检查一次
		Emitter.instance().notice_signal.connect(self.update_latest_event)

	def check_notice(self):
		if not self.if_backend_exist_event:
		# 	"""如果后端没有存储任何事件，不进行提醒"""
			return
		current = QDateTime.currentDateTime()
		if self.latest_event:
			notify_time = QDateTime.fromString(self.latest_event.advance_time, "yyyy-MM-dd HH:mm")
			log.info(f"{self.latest_event.title} - {self.latest_event.notes}-{notify_time}")
			if self.latest_event and current >= notify_time:
				log.info(f"提醒: {self.latest_event.title} - {self.latest_event.notes}")
				if sys.platform == "darwin":
					notify_mac(title='ChronosFlow', subtitle=self.latest_event.title,message=self.latest_event.notes)
				else:
					self.notify_show_floating_window.emit()
					self.notify_to_tray.emit((self.latest_event,))

				self.latest_event = None
				current = QDateTime.currentDateTime().addSecs(60)
				self.request_latest_event(current)

		else:
			self.request_latest_event(current)
			
	def update_latest_event(self, latest_event_info: tuple):
		tag = latest_event_info[1]
		if tag == "create":
			# 说明这是后端从零开始接受的第一条新消息
			self.if_backend_exist_event = True
			self.latest_event = latest_event_info[0]
			log.info(
				f"tag：{tag} 最新DDLEvent：{self.latest_event.title}; 提醒时间{self.latest_event.advance_time}; 截止时间{self.latest_event.datetime}")
		elif tag == "update":
			# 说明后端有更新，需要重新获取最新消息
			self.latest_event = latest_event_info[0]
			if self.latest_event:
				self.if_backend_exist_event = True
				log.info(f"tag：{tag} 最新DDLEvent：{self.latest_event.title}; 提醒时间{self.latest_event.advance_time}; 截止时间{self.latest_event.datetime}")		
			else:
				log.info(f"暂无DDLEvent")
				self.if_backend_exist_event = False	
		elif tag == "get":
			# 说明因提醒消耗了新消息，现在正在获取下一条最新消息
			if latest_event_info[0] is None:
				# 说明后端没有储存的当前时间以后的新日程了
				log.info(f"暂无DDLEvent")
				self.if_backend_exist_event = False
			else:
				self.latest_event = latest_event_info[0]
				self.if_backend_exist_event = True
				log.info(
					f"tag：{tag}最新DDLEvent：{self.latest_event.title}; 提醒时间{self.latest_event.advance_time}; 截止时间{self.latest_event.datetime}")
		"""把消息传递给悬浮窗以便于展示"""
		self.notify_to_floating_window.emit((self.latest_event,))

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

def notify_mac(title, subtitle, message):
	try:
		pync = get_pync()
		pync.notify(
			message,
			title = title,
			subtitle = subtitle,
			sound = "Ping"
		)
	except Exception as e:
		print(f"[通知失败] {e}")