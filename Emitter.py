from PySide6.QtCore import Signal, QObject


# 发射信号的类
class Emitter(QObject):
	# 定义信号
	dynamic_signal = Signal(object)  # 可接收任意参数
	page_change_signal = Signal(str)  # 向 main_stack发送改变页面的信号
	create_event_signal = Signal(str, str, str, str, str, str, str)  # 标签、路径、年、月（两位）、日（两位）、主题、内容
	search_signal = Signal(str)  # 发送sidebar搜索文本框的信息

	def __init__(self, parent=None):
		super().__init__(parent)

	def send_page_change_signal(self, name):
		"""
		向 main_stack发送改变页面的信号
		"""
		self.page_change_signal.emit(name)

	# TODO
	def send_create_event_signal(self, name, filename, year, month, day, theme, content):
		"""
		发射可变数量的字符串参数
		name为标签，如 create_event
		格式：标签、路径、年、月（两位）、日（两位）、主题、内容
		"""
		self.create_event_signal.emit(name, filename, year, month, day, theme, content)

	def send_search_signal(self, content):
		"""
		发送sidebar搜索文本框的信息
		"""
		self.search_signal.emit(content)

	def send_dynamic_signal(self, *args):
		"""
		发送格式不定的信号（元组形式）
		"""
		self.dynamic_signal.emit(args)
