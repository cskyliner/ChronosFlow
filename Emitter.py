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
	refresh_upcoming_signal: Signal = Signal()  # 在切换到Upcoming时更新
	refresh_upcoming_signal: Signal = Signal()  # 在切换到Upcoming时更新
	create_event_signal: Signal = Signal(object)  # 发送创建事件的信号
	search_signal: Signal = Signal(str)  # 发送sidebar搜索文本框的信息
	search_signal: Signal = Signal(str)  # 发送sidebar搜索文本框的信息
	modify_event_signal: Signal = Signal(object)  # 发送修改事件的信号
	storage_path_signal: Signal = Signal(object)  # 发送存储路径的信号
	view_and_edit_schedule_signal: Signal = Signal(object)  # 发送查看单条日程信号
	update_upcoming_event_signal: Signal = Signal(object)  # 向后端发送更新upcoming的回调信号
	delete_event_signal: Signal = Signal(object)  # 发送删除事件的信号
	search_all_event_signal: Signal = Signal(object)  # 向后端发送搜索全局事件的信号
	search_some_columns_event_signal: Signal = Signal(object)  # 向后端发送搜索部分列事件的信号
	search_time_event_signal: Signal = Signal(object)  # 向后端发送搜索时间范围内事件的信号
	backend_data_to_frontend_signal: Signal = Signal(object)  # 向前端发送后端数据的信号
	backend_data_to_frontend_signal: Signal = Signal(object)  # 向前端发送后端数据的信号
	notice_signal: Signal = Signal(object)  # 向通知栏发送最新数据
	latest_event_signal: Signal = Signal(object)  # 处理前端通知更新最新数据
	latest_event_signal: Signal = Signal(object)  # 处理前端通知更新最新数据

	@staticmethod
	def instance() -> "Emitter":
		if Emitter._instance is None:
			Emitter._instance = Emitter()
		return Emitter._instance

	def __init__(self):
		super().__init__()

	# ===转发信号函数====
	def send_refresh_upcoming_signal(self):
		self.refresh_upcoming_signal.emit()

	def send_page_change_signal(self, name):
		"""向 main_stack发送改变页面的信号"""
		self.page_change_signal.emit(name)

	def send_dynamic_signal(self, *args):
		"""发送格式不定的信号（元组形式）,只有一个对象也会变成元组"""
		self.dynamic_signal.emit(args)

	def send_view_and_edit_schedule_signal(self, data: tuple):
		"""data[0]是一个DDLEvent，储存显示信息；data[1]是告诉navigate_to的信号，再传给后端确保编辑某日程
  		之后原来的这条日程被覆盖"""
		self.view_and_edit_schedule_signal.emit(data)

	# ===转发数据函数====

	def send_backend_data_to_frontend_signal(self, data):
		"""向前端发送后端数据的信号，回传的是tuple[BaseEvent]"""
		log.info(f"发送后端数据到前端信号")
		self.backend_data_to_frontend_signal.emit(data)

	def send_notice_signal(self, data):
		"""向通知栏发送最新数据，回传数据为ddlevent"""
		log.info(f"向通知栏发送最新数据{data}")
		self.notice_signal.emit(data)

	# ===对接后端信号函数，发送信号第一个参数为命令====

	def send_storage_path(self, path):
		"""发送存储路径"""
		log.info(f"发送存储路径信号，存储路径为{path}")
		out = ("storage_path", path)
		self.storage_path_signal.emit(out)

	def send_create_event_signal(self, name, *args):
		"""
		name为event类型如 DDL
		*args代表name_event类对应的参数列表（元组）
		True代表是否添加到数据库（后端可能需要临时创建不添加到数据库的事件）
		最后和为元组形式
		"""
		log.info(f"发送创建事件或修改事件信号，事件类型为{name}，参数为{args}")
		out = ("create_event", name, True, *args)
		self.create_event_signal.emit(out)

	def send_modify_event_signal(self, id, name, *args):
		"""
		发送修改事件的信号
		id 为修改事件的id
		name为event类型如 DDL
		*args代表name_event类对应的参数列表（元组）
		"""
		log.info(f"发送修改事件的信号，事件ID为{id}，事件类型为{name}，参数为{args}")
		out = ("modify_event", id, name, *args)
		self.modify_event_signal.emit(out)

	def send_delete_event_signal(self, event_id: int, event_table_type: str):
		"""
		发送删除事件的信号
		event_id为事件ID
		event_type为事件类型
		"""
		log.info(f"发送删除事件的信号，事件ID为{event_id}，事件表名为{event_table_type}")
		out = ("delete_event", (event_id, event_table_type))
		self.delete_event_signal.emit(out)

	# ===向后端发送请求（回传数据），回调信号===

	def request_search_all_event_signal(self, keyword: tuple[str]):
		"""
		向后端发送搜索全局事件的请求
		keyword为搜索关键字，字符串元组
		"""
		log.info(f"向后端发送搜索全局事件的请求，搜索关键字为{keyword}")
		out = ("search_all", keyword)
		self.search_all_event_signal.emit(out)

	def request_update_upcoming_event_signal(self, start_pos: int, event_num: int):
		"""
		向后端发送更新upcoming的请求
		"""
		log.info(f"向后端发送更新upcoming的请求，参数为start_pos:{start_pos}，event_num:{event_num}")
		out = ("update_upcoming", (start_pos, event_num))
		self.update_upcoming_event_signal.emit(out)

	def request_search_time_event_signal(self, start_time: str, end_time: str):
		"""
		向后端发送搜索时间范围内事件的请求
		start_time和end_time为时间范围，字符串元组
		"""
		log.info(f"向后端发送搜索时间范围内事件的请求，搜索时间范围为{start_time}到{end_time}")
		out = ("search_time", (start_time, end_time))
		self.search_some_columns_event_signal.emit(out)

	def request_search_some_columns_event_signal(self, columns: tuple[str], keyword: tuple[str]):
		"""
		向后端发送搜索部分列中事件的请求
		"""
		log.info(f"向后端发送搜索部分列中事件的请求，搜索列为{columns}，关键字为{keyword}")
		out = ("search_some_columns", (columns, keyword))
		self.search_some_columns_event_signal.emit(out)

	def request_latest_event_signal(self, now_time: QDateTime):
		"""
		向后端发送需要更新最新的事件
		"""
		formatted_time = now_time.toString("yyyy-MM-dd HH:mm")
		log.info(f"向后端发送需要更新最新的事件，当前时间为{formatted_time}")
		out = ("latest_event", (formatted_time,))
		self.latest_event_signal.emit(out)
		out = ("latest_event", (formatted_time,))
		self.latest_event_signal.emit(out)
