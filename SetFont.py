from common import *

font0 = QFont()  # 用于普通的文字
font0.setFamilies(["Segoe UI", "Helvetica", "Arial"])
font0.setPointSize(12)

font1 = QFont()  # 用于较大的文字
font1.setFamilies(["Segoe UI", "Helvetica", "Arial"])
font1.setPointSize(15)


def common_set_font(my_widget, kind=0):
	"""
	设置init中有的字体字体
	"""
	if kind == 0:
		my_widget.setFont(font0)
	elif kind == 1:
		my_widget.setFont(font1)
