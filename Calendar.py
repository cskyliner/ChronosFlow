from common import *
from Event import DDLEvent
class CalendarDelegate(QStyledItemDelegate):
	def __init__(self, calendar=None, parent=None):
		super().__init__(parent)
		self.calendar = calendar
		self.base_font = QFont("Microsoft YaHei", 9)
		self.date_font = QFont("Microsoft YaHei", 10, QFont.Bold)  # 日期字体
		self.font_metrics = QFontMetrics(self.base_font)
		self.date_font_metrics = QFontMetrics(self.date_font)

		# 设置周末格式
		self.weekend_format = QTextCharFormat()
		self.weekend_format.setForeground(QColor("red"))

		self.event:list[DDLEvent] = []
		self.event_num = 0

	def paint(self, painter, option, index):
		super().paint(painter, option, index)  # 先进行常规绘制
		
		# 获取日期数据
		date = self.calendar.dateFromIndex(index)
		if not date.isValid():  # 表头或无效日期（如灰色的跨月日期）不处理
			return
		# 获取当前日历显示月份
		current_month = self.calendar.get_current_displayed_month()
		

		# 计算日期文本的精确位置和大小
		day_text = str(date.day())
		text_width = self.date_font_metrics.horizontalAdvance(day_text)
		text_height = self.date_font_metrics.height()
		
		# 计算文本居中的矩形区域
		text_rect = QRect(
			option.rect.x() + (option.rect.width() - text_width) // 2,
			option.rect.y() + (option.rect.height() - text_height) // 2,
			text_width,
			text_height
		)
	
		# 仅覆盖日期文本区域
		painter.save()
		painter.fillRect(text_rect, option.palette.base())
		painter.restore()

		# 仅在第一列添加"周"字
		if index.column() == 0:  # 第一列（周数列）
			painter.save()
			painter.setFont(self.date_font)
			painter.setPen(QColor("#666666"))  # 灰色文字
			painter.drawText(text_rect, Qt.AlignCenter, "周")
			painter.restore()

		#painter.fillRect(option.rect, option.palette.base())  # 用背景色覆盖默认日期位置
		painter.save()
		# 绘制日期（自定义位置）
		painter.setFont(self.date_font)
		
		if index.column() > 5:  # 周末
			painter.setPen(QColor("red"))
		else:
			painter.setPen(option.palette.text().color())

		# 绘制节假日标志
		if date in self.calendar.holidays:
			painter.save()
			painter.setPen(QColor("#4CAF50"))
			painter.setFont(QFont("Microsoft YaHei", 8, QFont.Bold))
			# 计算文本宽度，动态调整偏移（避免硬编码）

			text_width = self.font_metrics.horizontalAdvance("休")
			x_offset = 5  # 向左移动5像素（可调整）
			painter.drawText(
				option.rect.x() + option.rect.width() - 15,  # 左边界 + 偏移
				option.rect.y() + 2,  # 顶部偏移
				option.rect.width() - text_width - x_offset,  # 剩余宽度
				option.rect.height(),
				Qt.AlignTop,  # 仅顶部对齐，左对齐默认
				"休"
			)
			painter.restore()
		
		# 在单元格顶部绘制日期
		date_rect = QRect(
			option.rect.x() + (option.rect.width() - self.date_font_metrics.horizontalAdvance(day_text)) / 2,
			option.rect.y() + 2,
			self.date_font_metrics.horizontalAdvance(day_text),
			self.date_font_metrics.height()
		)
		painter.drawText(date_rect, Qt.AlignCenter, day_text)
		painter.restore()

		# 绘制日程（从日期下方开始）
		events = self.calendar.schedules.get(date, [])

		if events :
			pos = (index.row() - 1) * 7 + index.column() - 1
			date_obj = datetime.strptime(events[0].datetime, "%Y-%m-%d %H:%M")
			month = date_obj.month
			month_int = int(month)	
			if abs(pos - date.day()) < 20  :
				painter.save()
				painter.setFont(self.base_font)
				painter.setPen(QColor("#333333"))
				
				# 计算日程起始位置（从日期文本的下一行开始）
				date_bottom = option.rect.y() + 2 + self.date_font_metrics.height()  # 日期底部坐标
				y_pos = date_bottom + 10  # 日程顶部与日期底部保持5px间距
				
				line_height = self.font_metrics.height() + 1  # 每行高度（含间距）
				
				for i, event in enumerate(events[:]):
					painter.drawText(
						option.rect.x() + (option.rect.width() - self.font_metrics.horizontalAdvance(event.title)) / 2 - 8,  # 左侧缩进5px
						y_pos + i * line_height,  # 垂直位置逐行增加
						f"• {event.title}"
					)
				
				painter.restore()
		# 绘制边框
		painter.save()
		painter.setPen(QPen(QColor("#bbdefb"), 1))
		painter.drawRect(option.rect.adjusted(0, 0, -1, -1))
		painter.restore()
		


	def sizeHint(self, option, index):
		size = super().sizeHint(option, index)
		date = self.calendar.dateFromIndex(index)
		
		if isinstance(date, QDate) and date.isValid():
			events = self.calendar.schedules.get(date, [])
			line_height = self.font_metrics.height() + 1  # 增加行间距
			#size.setHeight(max(80, 20 + self.date_font_metrics.height() + min(len(events), 10) * line_height))
			size.setHeight(max(80, 20 + self.date_font_metrics.height() + len(events) * line_height))
		return size

class Calendar(QCalendarWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.hover_date = QDate()
		self.setMouseTracking(True)
		self.holidays = set()
		holidays_2025 = [
		QDate(2025, 1, 28), QDate(2025, 1, 29), QDate(2025, 1, 30), QDate(2025, 1, 31),
		QDate(2025, 2, 1), QDate(2025, 2, 2), QDate(2025, 2, 3), QDate(2025, 2, 4),  # 春节
		QDate(2025, 4, 4),  # 清明节
		QDate(2025, 5, 31), QDate(2025, 6, 1), QDate(2025, 6, 2),  # 端午节
		QDate(2025, 10, 1), QDate(2025, 10, 2), QDate(2025, 10, 3), QDate(2025, 10, 4),
		QDate(2025, 10, 5), QDate(2025, 10, 6), QDate(2025, 10, 7),  # 国庆节
		QDate(2025, 10, 6), QDate(2025, 10, 7), QDate(2025, 10, 8)  # 中秋节
		]
		self.schedules = defaultdict(list)

		self.add_holiday(*holidays_2025)
		self.setStyleSheet("""
					Calendar QAbstractItemView:enabled {     /*禁用选中高亮效果*/
						selection-background-color: transparent;  /* 透明背景 */
						selection-color: palette(text);        /* 使用正常文本颜色 */
					}
					QCalendarWidget QAbstractItemView {   /*消除边框*/
						border: none;
						outline: 0;
						selection-background-color: transparent;
					}
					QCalendarWidget QAbstractItemView:item:hover {  /*鼠标悬停*/
						background-color: palette(midlight);
					}
				""")
		self.init_ui()

	
	def get_current_displayed_month(self):
		return self.selectedDate().month()
	def init_ui(self):
		# 配置视图
		if table_view := self.findChild(QTableView):
			table_view.setItemDelegate(CalendarDelegate(self))
			table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
			# 设置垂直表头（周数列）样式
			table_view.verticalHeader().setStyleSheet("""
				QHeaderView::section {
					background-color: #F0F0F0;  /* 浅灰色背景 */
					color: #666666;             /* 深灰色文字 */
					border-right: 1px solid #D3D3D3; /* 右侧分隔线 */
					padding: 5px;
					min-width: 30px;
				}
			""")
			table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
	def dateFromIndex(self, index):
		""" 安全获取日期的方法 """
		year = self.yearShown()
		month = self.monthShown()
		day = index.data(Qt.DisplayRole)
		
		if isinstance(day, int) and 1 <= day <= 31:
			return QDate(year, month, day)
		return QDate()
	def add_holiday(self, *dates):
		for date in dates:
			self.holidays.add(date)
		self.updateCells()

	def add_schedule(self, date, event:DDLEvent):
		self.schedules[date].append(event)
		self.updateCells()