from PySide6.QtCore import Signal, QObject
from common import logging

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
	search_all_event_signal: Signal = Signal(object)  # 向后端发送搜索全局事件的信号
	search_some_columns_event_signal: Signal = Signal(object)  # 向后端发送搜索部分列的事件
	signal_to_schedule_notice: Signal = Signal(str, str, int, str)  # 向Notice中的schedule_notice函数发送信号

	@staticmethod
	def instance() -> "Emitter":
		if Emitter._instance is None:
			Emitter._instance = Emitter()
		return Emitter._instance

	def __init__(self):
		super().__init__()

	# ===转发信号函数====
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

	# ===对接后端信号函数，发送信号第一个参数为命令====
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

	def send_search_all_event_signal(self, keyword: tuple[str]):
		"""
		向后端发送搜索全局事件的信号
		keyword为搜索关键字，字符串元组
		"""
		log.info(f"send search all event signal，搜索关键字为{keyword}")
		out = ("search_all", keyword)
		self.search_all_event_signal.emit(out)

	def send_search_some_columns_event_signal(self, columns: tuple[str], keyword: tuple[str]):
		"""
		向后端发送搜索部分列的事件
		"""
		log.info(f"send search some columns event signal，搜索列为{columns}，关键字为{keyword}")
		out = ("search_some_columns", columns, keyword)
		self.search_some_columns_event_signal.emit(out)
