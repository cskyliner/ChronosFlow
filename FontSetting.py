from common import *
from PySide6.QtGui import QFont

log = logging.getLogger("FontSetting")

common_font = QFont()  # 用于普通的文字，0
common_font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
common_font.setPointSize(13)

big_font = QFont()  # 用于较大的文字，1
big_font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
big_font.setPointSize(15)

title_font = QFont()  # 用于应用名的字体，2
title_font.setFamilies(["Inter", "Helvetica Neue", "Segoe UI", "Arial"])
title_font.setPointSize(20)

delete_font = QFont()  # 用于Upcoming中完成的日程,3
delete_font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
delete_font.setPointSize(13)
delete_font.setStrikeOut(True)

one_day_font=QFont()
one_day_font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
one_day_font.setPixelSize(20)
one_day_font.setItalic(False)


def set_font(my_widget, kind=0):
	"""
	设置init中有的字体字体，以常用程度排序
	"""
	if kind == 0:
		my_widget.setFont(common_font)
	elif kind == 1:
		my_widget.setFont(big_font)
	elif kind == 2:
		my_widget.setFont(title_font)
	elif kind == 3:
		my_widget.setFont(delete_font)
	elif kind==4:
		my_widget.setFont(one_day_font)
	else:
		log.error("警告：使用未知字体！")


def reset_font(size0, size1, size2):
	"""
	Setting中重设字体大小
	:param size: 字体大小
	"""
	pass
