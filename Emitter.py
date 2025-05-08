from PySide6.QtCore import Signal, QObject
from common import *
log = logging.getLogger(__name__)


# 发射信号的类
class Emitter(QObject):
	'''
	通用信号发射器
	'''
	_instance = None  # 唯一实例
	dynamic_signal: Signal = Signal(object)  # 可接收任意参数
	page_change_signal: Signal = Signal(str)  # 向 main_stack发送改变页面的信号
	create_event_signal: Signal = Signal(object)  # 发送创建事件的信号
	search_signal: Signal = Signal(str)  # 发送sidebar搜索文本框的信息
	storage_path_signal: Signal = Signal(object)  # 发送存储路径的信号
	search_all_event_signal: Signal = Signal(object)  # 向后端发送搜索全局事件的信号
	search_some_columns_event_signal: Signal = Signal(object)  # 向后端发送搜索部分列事件的信号
	update_upcoming_event_signal:Signal = Signal(object)  # 向后端发送更新upcoming的信号
	search_time_event_signal: Signal = Signal(object)  # 向后端发送搜索时间范围内事件的信号
	backend_data_to_frontend_signal: Signal = Signal(object)  # 向前端发送后端数据的信号
	signal_to_schedule_notice: Signal = Signal(str, str, QDateTime, str)  # 向Notice中的schedule_notice函数发送信号
	from_upcoming_to_create_event_signal: Signal = Signal(str,str) #从upcoming跳转到create_event
	refresh_upcoming_signal: Signal = Signal(str)
	@staticmethod
	def instance() -> "Emitter":
		if Emitter._instance is None:
			Emitter._instance = Emitter()
		return Emitter._instance

	def __init__(self):
		super().__init__()

	# ===转发信号函数====
	def send_refresh_upcoming_signal(self,title):
		self.refresh_upcoming_signal.emit(title)
	def send_page_change_signal(self, name):
		"""向 main_stack发送改变页面的信号"""
		self.page_change_signal.emit(name)

	def send_search_signal(self, content):
		"""发送sidebar搜索文本框的信息"""
		self.search_signal.emit(content)

	def send_dynamic_signal(self, *args):
		"""发送格式不定的信号（元组形式）,只有一个对象也会变成元组"""
		self.dynamic_signal.emit(args)

	def send_signal_to_schedule_notice(self, title, content, notify_time, color="#3498db"):
		"""向Notice中的schedule_notice函数发送信号"""
		self.signal_to_schedule_notice.emit(title, content, notify_time, color)

	def send_from_upcoming_to_create_event_signal(self,theme,date):
		"""从upcoming跳转到create_event"""
		#TODO:如何确定是哪一个日程（哈希的标准是什么）
		self.from_upcoming_to_create_event_signal.emit(theme,date)

	# ===转发数据函数====

	def send_backend_data_to_frontend_signal(self, data):
		"""向前端发送后端数据的信号，回传的是tuple[BaseEvent]"""
		log.info(f"发送后端数据到前端信号")
		self.backend_data_to_frontend_signal.emit(data)

	# ===对接后端信号函数，发送信号第一个参数为命令====
	
	def send_storage_path(self, path):
		"""发送存储路径"""
		log.info(f"send storage path signal，存储路径为{path}")
		out = ("storage_path", path)
		self.storage_path_signal.emit(out)

	def send_create_event_signal(self, name, *args):
		"""
		name为event类型如 DDL
		*args代表name_event类对应的参数列表（元组）
		True代表是否添加到数据库（后端可能需要临时创建不添加到数据库的事件）
		最后和为元组形式
		"""
		log.info(f"send create event signal，事件类型为{name}，参数为{args}")
		out = ("create_event", name, True, *args)
		self.create_event_signal.emit(out)

	# ===向后端发送请求（回传数据）===

	def request_search_all_event_signal(self, keyword: tuple[str]):
		"""
		向后端发送搜索全局事件的请求
		keyword为搜索关键字，字符串元组
		"""
		log.info(f"request search all event，搜索关键字为{keyword}")
		out = ("search_all", keyword)
		self.search_all_event_signal.emit(out)

	def request_update_upcoming_event_signal(self,start_pos:int, event_num:int):
		"""
		向后端发送更新upcoming的请求
		"""
		log.info(f"request update upcoming event，参数为start_pos:{start_pos}，event_num:{event_num}")
		out = ("update_upcoming", (start_pos,event_num))
		self.update_upcoming_event_signal.emit(out)

	def request_search_time_event_signal(self, start_time:str, end_time:str):
		"""
		向后端发送搜索时间范围内事件的请求
		start_time和end_time为时间范围，字符串元组
		"""
		log.info(f"request search time event，搜索时间范围为{start_time}到{end_time}")
		out = ("search_time", (start_time, end_time))
		self.search_some_columns_event_signal.emit(out)

	def request_search_some_columns_event_signal(self, columns: tuple[str], keyword: tuple[str]):
		"""
		向后端发送搜索部分列中事件的请求
		"""
		log.info(f"request search some columns event，搜索列为{columns}，关键字为{keyword}")
		out = ("search_some_columns", (columns, keyword))
		self.search_some_columns_event_signal.emit(out)