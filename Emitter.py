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
	dynamic_signal = Signal(object)  # 使用 object 类型接收任意参数

	def send_signal(self, *args):
		#发射可变数量的字符串参数
		self.dynamic_signal.emit(args)  # 将参数打包为元组发射