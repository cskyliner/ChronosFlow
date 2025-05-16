from common import *

log = logging.getLogger("Setfont")

common_font = QFont()  # 用于普通的文字
common_font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
common_font.setPointSize(12)

big_font = QFont()  # 用于较大的文字
big_font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
big_font.setPointSize(15)

title_font = QFont()
title_font.setFamilies(["Inter", "Helvetica Neue", "Segoe UI", "Arial"])
title_font.setPointSize(20)


def common_set_font(my_widget, kind=0):
	"""
	设置init中有的字体字体
	"""
	if kind == 0:
		my_widget.setFont(common_font)
	elif kind == 1:
		my_widget.setFont(big_font)
	elif kind == 2:
		my_widget.setFont(title_font)
	else:
		log.error("警告：使用未知字体！")
