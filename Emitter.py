from PySide6.QtCore import Signal, QObject


# 发射信号的类
class Emitter(QObject):
	def __init__(self, parent=None):
		super().__init__(parent)

		# 信号管理集，管理信号
		self.signals = {}

	# 添加信号
	def add_signal(self, name):
		if not name in self.signals:
			# 动态将信号添加到类中
			setattr(self.__class__, name, Signal(str))
			self.signals[name] = getattr(self, name)
		else:
			print(f"{name}已存在！")

	# 发送信号
	def send_signal(self, name):
		if name in self.signals:
			self.signals[name].emit(name)
		else:
			print(f"信号{name}未定义！")


class TempEmitter(QObject):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.signal1 = Signal(str)
		self.signal3 = Signal(str, str, str)

	def send_signal1(self, s):
		self.signal1.emit(s)

	def send_signal3(self, s1, s2, s3):
		self.signal3.emit(s1, s2, s3)
