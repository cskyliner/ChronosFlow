from common import *
from Event import DDLEvent
from Event import DDLEvent
if sys.platform == 'darwin':
	import pync
log = logging.getLogger(__name__)
from Emitter import Emitter
from Emitter import Emitter

class Notice(QObject):
	notify_to_floating_window = Signal(object)  # 向悬浮窗发送通知信号(标题，内容，颜色代码)
	notify_to_tray = Signal(object)  # 向托盘发送通知信号(标题，内容，颜色代码)
	notify_to_floating_window = Signal(object)  # 向悬浮窗发送通知信号(标题，内容，颜色代码)
	notify_to_tray = Signal(object)  # 向托盘发送通知信号(标题，内容，颜色代码)
	notify_show_floating_window = Signal()
	notify_to_backend = Signal()

	notify_to_backend = Signal()

	def __init__(self):
		super().__init__()
		self.scheduled_notices = []  # 存储计划通知
		self.if_backend_exist_event = True
		self.latest_event:DDLEvent = None
		self.if_backend_exist_event = True
		self.latest_event:DDLEvent = None
		self.timer = QTimer()
		#self.timer.timeout.connect(self.check_notices)
		self.timer.timeout.connect(self.check_notice)
		self.timer.start(1000)  # 每秒检查一次
		Emitter.instance().notice_signal.connect(self.update_latest_event)

	def check_notice(self):
		if not self.if_backend_exist_event:
			"""如果后端没有存储任何事件，不进行提醒"""
			log.info(f"后端没有储存任何事件，不进行提醒")
			return
		current = QDateTime.currentDateTime()
		if self.latest_event:
			log.info(f"当前Notice储存最新事件{self.latest_event.title}；提醒时间{self.latest_event.advance_time}")
			notify_time = QDateTime.fromString(self.latest_event.advance_time, "yyyy-MM-dd HH:mm")
			if self.latest_event and current >= notify_time:
				log.info(f"提醒: {self.latest_event.title} - {self.latest_event.notes}")
				if sys.platform == "darwin":
					pync.notify(self.latest_event.notes, title='ChronosFlow', subtitle=self.latest_event.title, sound='Ping')
				else:
					self.notify_show_floating_window.emit()
					self.notify_to_floating_window.emit((self.latest_event,))
					self.notify_to_tray.emit((self.latest_event,))

				self.latest_event = None
				current = QDateTime.currentDateTime().addSecs(60)
				self.request_latest_event(current)

		else:
			log.info(f"当前Notice没有储存事件，正调用request_latest_event获取事件")
			self.request_latest_event(current)

	def update_latest_event(self, latest_event_info:tuple):
		tag = latest_event_info[1]
		if tag == "create":
			#说明这是后端从零开始接受的第一条新消息
			self.if_backend_exist_event = True
			self.latest_event = latest_event_info[0]
			log.info(f"tag：{tag} 最新DDLEvent：{self.latest_event.title}; 提醒时间{self.latest_event.advance_time}; 截止时间{self.latest_event.datetime}")		
		elif tag == "update":
			#说明后端有更新，需要重新获取最新消息
			self.latest_event = latest_event_info[0]
			log.info(f"tag：{tag} 最新DDLEvent：{self.latest_event.title}; 提醒时间{self.latest_event.advance_time}; 截止时间{self.latest_event.datetime}")			
		elif tag == "get":
			#说明因提醒消耗了新消息，现在正在获取下一条最新消息
			if latest_event_info[0] is None:
				#说明后端没有储存的当前时间以后的新日程了
				log.info(f"暂无DDLEvent")
				self.if_backend_exist_event = False
			else:
				self.latest_event = latest_event_info[0]
				log.info(f"tag：{tag}最新DDLEvent：{self.latest_event.title}; 提醒时间{self.latest_event.advance_time}; 截止时间{self.latest_event.datetime}")
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
			font-size: 12px;
			color: #2c3e50;
		""")
		layout.addWidget(content_label)

		self.setLayout(layout)

	def _start_close_timer(self):
		"""8秒后自动关闭"""
		QTimer.singleShot(8000, self.close)
