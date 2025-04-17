from PySide6.QtWidgets import QCalendarWidget, QMenu, QInputDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption


class Calendar(QCalendarWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.notes = {}  # 存储每日文本 {QDate: str}TODO:与后端数据库连接
		self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.customContextMenuRequested.connect(self.show_context_menu)

	def paintCell(self, painter, rect, date):
		"""重写绘制单元格方法"""
		super().paintCell(painter, rect, date)
		painter.drawRect(rect)
		# 如果有该日期的文本，则绘制
		if date in self.notes:
			painter.save()
			# 设置小字体
			font = painter.font()
			font.setPointSize(8)
			painter.setFont(font)

			# 设置文本选项（自动换行）
			option = QTextOption()
			option.setWrapMode(QTextOption.WrapMode.WordWrap)
			option.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

			# 调整矩形区域，留出空间
			text_rect = rect.adjusted(2, 2, -2, -2)

			# 绘制文本
			painter.drawText(text_rect, self.notes[date], option)
			painter.restore()

	def show_context_menu(self, pos):
		"""显示右键菜单"""
		# 获取当前选中的日期（而不是点击位置的日期）FIXME：这里可能需要商榷
		date = self.selectedDate()

		menu = QMenu(self)

		add_action = menu.addAction("添加/编辑日程")
		clear_action = menu.addAction("清除日程")

		action = menu.exec(self.mapToGlobal(pos))

		if action == add_action:
			text, ok = QInputDialog.getText(
				self, "输入时间",
				f"为 {date.toString('yyyy-MM-dd')} 添加时间:",
				text=self.notes.get(date, "")
			)
			if ok and text:
				self.notes[date] = text
				self.updateCells()

		elif action == clear_action and date in self.notes:
			del self.notes[date]
			self.updateCells()
