from src.common import *
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem, QSizePolicy
from PySide6.QtCore import QRectF
from events.EventManager import *
from events.EventManager import EventSQLManager

log = logging.getLogger(__name__)


def get_month_range(year: int, month: int):
	"""
	获取每页的起止时间
	"""
	first_day = QDate(year, month, 1)
	start_offset = first_day.dayOfWeek() - 1  # 从开始的第一周的周一
	start_date = first_day.addDays(-start_offset)
	end_date = start_date.addDays(41)  # 到最后补齐42个格
	return start_date, end_date


class CalendarDayItem(QObject, QGraphicsRectItem):
	"""
	单元格
	"""
	clicked = Signal(QDate)
	right_clicked = Signal(QDate, QPoint)
	double_clicked = Signal(QDate)

	def __init__(self, rect: QRectF, date: QDate, is_current_month: bool, is_today: bool, events: list[BaseEvent]):
		QObject.__init__(self)
		QGraphicsRectItem.__init__(self, rect)
		self.date = date
		self.is_current_month = is_current_month
		self.is_today = is_today
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		self.setAcceptHoverEvents(True)
		self._hovering = False
		self._selected = False
		self.event: list[BaseEvent] = events

	def hoverEnterEvent(self, event):
		self._hovering = True
		self.update()

	def hoverLeaveEvent(self, event):
		self._hovering = False
		self.update()

	def mousePressEvent(self, event):
		self._pressed_inside = self.contains(event.pos())
		super().mousePressEvent(event)

	def mouseDoubleClickEvent(self, event):
		modifiers = QApplication.keyboardModifiers()
		if event.button() == Qt.LeftButton and not (modifiers & Qt.ShiftModifier):
			self.double_clicked.emit(self.date)
		super().mouseDoubleClickEvent(event)

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton and getattr(self, "_pressed_inside", False) and self.contains(event.pos()):
			view = self.scene().views()[0]
		modifiers = QApplication.keyboardModifiers()
		shift_pressed = modifiers & Qt.ShiftModifier

		if not shift_pressed:
			# 不按Shift，清除其他选中，只选中当前
			if hasattr(view, "clear_selection"):
				view.clear_selection()
			self._selected = True
		else:
			# 按住Shift，切换当前选中状态
			self._selected = not self._selected
		self.update()

	def contextMenuEvent(self, event):
		global_pos = event.screenPos()
		self.right_clicked.emit(self.date, global_pos)
		log.info("用户点击右键，弹出菜单")

	def paint(self, painter, option, widget=None):
		palette = QApplication.palette()  # 获取主题
		# 根据主题设置颜色
		background_color = palette.color(QPalette.Base)  # 背景色（适配主题）
		btn_color = palette.color(QPalette.Button)  # 按钮背景色
		light_color = palette.color(QPalette.Highlight)
		if self._selected:  # 选中
			painter.setBrush(QBrush(light_color))
		elif self._hovering:  # 悬浮
			painter.setBrush(QBrush(light_color))
		else:
			painter.setBrush(QBrush(background_color) if self.is_current_month else QBrush(btn_color))

		text_color = palette.color(QPalette.Text)
		mid_color = palette.color(QPalette.Mid)
		painter.setPen(QPen(mid_color))  # 边框颜色
		painter.drawRect(self.rect())
		painter.setPen(QColor("#1E90FF") if self.is_today else QPen(text_color))  # 日期的颜色
		if self.date.day() == 1:
			rect = self.rect()
			# 月份字体较大
			font_month = painter.font()
			font_month.setPointSizeF(font_month.pointSizeF() * 1.4)
			font_month.setBold(True)
			month_text = f"{self.date.month()}月"
			painter.setFont(font_month)
			month_metrics = QFontMetrics(font_month)
			month_width = month_metrics.horizontalAdvance(month_text)
			# 日期字体较小
			font_day = painter.font()
			font_day.setPointSizeF(font_day.pointSizeF() * 0.7)
			font_day.setBold(False)
			painter.setFont(font_day)
			day_text = "1"
			day_metrics = QFontMetrics(font_day)
			day_width = day_metrics.horizontalAdvance(day_text)
			# 使日号“1”居中
			x_day = rect.x() + (rect.width() - day_width) / 2
			x_month = x_day - month_width - 4
			# 水平对齐基准线
			y_base_month = rect.y() + 6 + month_metrics.ascent()
			y_base_day = rect.y() + 6 + day_metrics.ascent()
			y_base = max(y_base_month, y_base_day)

			painter.setFont(font_month)
			painter.drawText(QPointF(x_month, y_base), month_text)
			painter.setFont(font_day)
			painter.drawText(QPointF(x_day, y_base), day_text)
		else:
			text = str(self.date.day())
			rect = self.rect().adjusted(0, 10, 0, 0)  # 顶部留一定间距以求美观
			painter.drawText(rect, Qt.AlignHCenter | Qt.AlignTop, text)

		# 绘制事件列表，最多3条
		max_events_to_show = 3
		event_area_rect = self.rect().adjusted(4, 24, -4, -4)

		# 根据格子高度动态调整字体大小
		cell_height = self.rect().height()
		dynamic_font_size = max(6, min(12, int(cell_height * 0.13)))

		font = painter.font()
		font.setPointSize(dynamic_font_size)
		painter.setFont(font)

		font_metrics = QFontMetrics(font)
		line_height = font_metrics.lineSpacing()

		x = event_area_rect.left()
		y = event_area_rect.top() + line_height

		bg_colors = (QColor(225, 160, 125), QColor(230, 205, 145), QColor(140, 175, 195), QColor(150, 165, 135))  # 循环颜色

		for i, event in enumerate(self.event[:max_events_to_show]):
			# 计算当前日程条目的背景矩形区域
			bg_rect = QRectF(
				event_area_rect.left(),
				event_area_rect.top() + i * line_height,
				event_area_rect.width(),
				line_height
			)

			# 绘制圆角背景矩形
			painter.setPen(Qt.NoPen)  # 无边框
			painter.setBrush(QBrush(bg_colors[i % 3]))
			painter.drawRoundedRect(bg_rect, 4, 4)  # 4px圆角

			# 绘制文字
			painter.setPen(QPen(text_color))
			elided_text = font_metrics.elidedText(event.title, Qt.ElideRight, int(event_area_rect.width()))
			painter.drawText(bg_rect, Qt.AlignLeft | Qt.AlignVCenter, " " + elided_text)  # 左侧加空格留边距

		event_count = len(self.event)
		# 超过三条显示更多
		metrics = QFontMetrics(font)
		line_h = metrics.lineSpacing()
		if event_count > max_events_to_show:
			# 计算背景矩形区域
			bg_rect = QRectF(
				event_area_rect.left(),
				event_area_rect.top() + max_events_to_show * line_h,
				event_area_rect.width(),
				line_h
			)

			painter.setPen(Qt.NoPen)
			painter.setBrush(QBrush(bg_colors[3]))  # 绿色
			painter.drawRoundedRect(bg_rect, 4, 4)

			more_font = QFont(font)
			more_font.setPointSize(font.pointSize() - 1)
			more_font.setItalic(True)
			painter.setFont(more_font)
			painter.setPen(QPen(text_color))  # "更多"的颜色

			text = f"更多 ({event_count - max_events_to_show})..."
			painter.drawText(bg_rect, Qt.AlignRight | Qt.AlignVCenter, text)


class CalendarView(QWidget):
	"""
	新日历
	"""
	double_clicked = Signal(QDate)
	view_single_day = Signal(QDate)

	def __init__(self):
		super().__init__()
		# 日程信息
		self.schedules = defaultdict(list)
		# 绑定快捷键
		self.setFocusPolicy(Qt.StrongFocus)
		QShortcut(QKeySequence(Qt.Key_Left), self, self.go_to_prev_month)
		QShortcut(QKeySequence(Qt.Key_Right), self, self.go_to_next_month)
		QShortcut(QKeySequence(Qt.Key_Home), self, self.go_to_today)

		layout = QVBoxLayout(self)  # 整体布局
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		title_layout = QHBoxLayout()  # 标题布局
		self.title_label = QLabel()  # 显示当前年月
		self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		# 设置标题初始字体
		font = QFont()
		font.setPointSize(18)
		font.setBold(True)
		self.title_label.setFont(font)
		btn_layout = QHBoxLayout()  # 切换月份按钮布局
		common_btn_style = """
			QPushButton {
				border: none;
				background-color: palette(midlight);
				padding: 4px 12px;
				border-radius: 4px;
			}
			QPushButton:hover {
				background-color: palette(light);
			}
			QPushButton:pressed {
				background-color: palette(mid);
			}
		"""
		self.prev_btn = QPushButton("〈")
		self.today_btn = QPushButton("Today")
		self.next_btn = QPushButton("〉")
		self.prev_btn.setStyleSheet(common_btn_style)
		self.today_btn.setStyleSheet(common_btn_style)
		self.next_btn.setStyleSheet(common_btn_style)
		self.prev_btn.clicked.connect(self.go_to_prev_month)
		self.today_btn.clicked.connect(self.go_to_today)
		self.next_btn.clicked.connect(self.go_to_next_month)

		btn_layout.addWidget(self.prev_btn)
		btn_layout.addWidget(self.today_btn)
		btn_layout.addWidget(self.next_btn)

		title_layout.addWidget(self.title_label)
		title_layout.addStretch()
		title_layout.addLayout(btn_layout)
		layout.addLayout(title_layout)

		self.view = QGraphicsView()
		self.view.setFrameStyle(QFrame.NoFrame)
		self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
		self.scene = QGraphicsScene()
		self.view.setScene(self.scene)
		self.view.setRenderHints(self.view.renderHints() | QPainter.Antialiasing)
		self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
		self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.view.clear_selection = self.clear_selection
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
		layout.addWidget(self.view)

		self.current_year = QDate.currentDate().year()
		self.current_month = QDate.currentDate().month()
		self.update_title()
		self.handle_page_changed(self.current_year, self.current_month)

	# 控制draw_month出发时间，避免第一次初始化时候在resize前draw
	def showEvent(self, event):
		super().showEvent(event)
		QTimer.singleShot(0, self._delayed_draw)

	def _delayed_draw(self):

		# 更新标题字体
		base_width = 700
		scale = max(min(self.width() / base_width, 2.0), 0.6)  # 缩放范围限制
		font_size = int(16 * scale)
		font_size = max(12, min(font_size, 28))  # 限定字号范围

		font = QFont()
		font.setPointSize(font_size)
		font.setBold(True)
		self.title_label.setFont(font)

		# 动态设置按钮字体大小
		btn_font_size = int(12 * scale)
		btn_font_size = max(10, min(btn_font_size, 20))
		btn_font = QFont()
		btn_font.setPointSize(btn_font_size)
		self.prev_btn.setFont(btn_font)
		self.today_btn.setFont(btn_font)
		self.next_btn.setFont(btn_font)

		# 更新日历栏大小
		# 自适应高宽
		w = self.view.viewport().width()
		h = self.view.viewport().height()
		day_width = w / 7
		weekday_height = 30  # 固定周几栏高度
		day_height = (h - weekday_height) / 6  # 剩余高度分给日期		
		total_cols = 7
		total_rows = 6
		self.scene.setSceneRect(0, 0, total_cols * day_width, weekday_height + total_rows * day_height)
		self.draw_month(self.current_year, self.current_month)
		self.view.resetTransform()

	def update_title(self):
		self.title_label.setText(f"{self.current_year}年{self.current_month}月")

	def resizeEvent(self, event):
		super().resizeEvent(event)
		QTimer.singleShot(0, self._delayed_draw)	

		print("sceneRect:", self.scene.sceneRect())
		print("viewport size:", self.view.viewport().size())
		bound = self.scene.itemsBoundingRect()
		print("itemsBoundingRect:", bound)

	def clear_selection(self):
		for item in self.scene.items():
			if isinstance(item, CalendarDayItem):
				item._selected = False
				item.update()

	def draw_month(self, year, month, day_width=None, day_height=None):
		self.scene.clear()
		start_date, end_date = get_month_range(year, month)

		if day_width is None:
			day_width = self.view.width() / 7
		if day_height is None:
			day_height = self.view.height() / 6
		# 添加周几栏（固定在顶部）
		weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
		weekday_height = 30  # 周几栏高度
		for col in range(7):
			palette = QApplication.palette()
			background_color = palette.color(QPalette.Button)  # 背景色（适配主题）
			text_color = palette.color(QPalette.Text)
			rect = QRectF(col * day_width, 0, day_width, weekday_height)
			weekday_item = QGraphicsRectItem(rect)
			weekday_item.setBrush(QBrush(background_color))  # 浅灰色背景
			weekday_item.setPen(QPen(Qt.NoPen))
			self.scene.addItem(weekday_item)

			# 添加周几文本
			text_item = QGraphicsSimpleTextItem(weekday_names[col], weekday_item)
			text_item.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
			text_item.setBrush(QBrush(text_color))  # 深灰色文字
			# 文本居中
			text_width = text_item.boundingRect().width()
			text_item.setPos(rect.x() + (rect.width() - text_width) / 2, rect.y() + 5)
		col = 0
		row = 0
		today = QDate.currentDate()

		current = QDate(start_date)
		while current < end_date.addDays(1):
			rect = QRectF(col * day_width, weekday_height + row * day_height, day_width, day_height)
			item = CalendarDayItem(
				rect=rect,
				date=current,
				is_current_month=(current.month() == month),
				is_today=(current == today),
				events=self.schedules[current]
			)
			# item.clicked.connect(self.date_clicked.emit)
			item.right_clicked.connect(self.handle_right_click)
			item.double_clicked.connect(self.double_clicked.emit)
			self.scene.addItem(item)
			col += 1
			if col == 7:
				col = 0
				row += 1
			current = current.addDays(1)

		total_cols = 7
		total_rows = 7
		# self.scene.setSceneRect(0, 0, total_cols * day_width, total_rows * day_height)
		self.scene.setSceneRect(0, 0, total_cols * day_width, weekday_height + (total_rows - 1) * day_height)


	def go_to_month(self, year: int, month: int):
		self.current_year = year
		self.current_month = month
		self.handle_page_changed(self.current_year, self.current_month)
		self.draw_month(year, month)
		self.update_title()

	def go_to_prev_month(self):
		log.info("上一月")
		if self.current_month == 1:
			self.current_month = 12
			self.current_year -= 1
		else:
			self.current_month -= 1
		self.handle_page_changed(self.current_year, self.current_month)
		self.draw_month(self.current_year, self.current_month)
		self.update_title()

	def go_to_next_month(self):
		log.info("下一月")
		if self.current_month == 12:
			self.current_month = 1
			self.current_year += 1
		else:
			self.current_month += 1
		self.handle_page_changed(self.current_year, self.current_month)
		self.draw_month(self.current_year, self.current_month)
		self.update_title()

	def go_to_today(self):
		log.info("回到今天")
		today = QDate.currentDate()
		self.current_year = today.year()
		self.current_month = today.month()
		self.handle_page_changed(today.year(), today.month())
		self.go_to_month(today.year(), today.month())

	def clear_selection(self):
		for item in self.scene.items():
			if isinstance(item, CalendarDayItem):
				item._selected = False
				item.update()

	def add_schedule(self, event: BaseEvent):
		date = QDate.fromString(event.datetime.split(" ")[0], "yyyy-MM-dd")
		self.schedules[date].append(event)

	def handle_page_changed(self, year: int, month: int):
		"""月份或年份变化时的回调"""
		log.info(f"页面切换至: {year}年{month}月")
		events = EventSQLManager.get_events_in_month(year, month)
		if events is not None and len(events) > 0:
			log.info(f"接收数据成功，共接收 {len(events)} 条数据：\n" +
					"\n".join(f"- {event.title} @ {event.datetime}" for event in events))
		self.schedules.clear()
		for event in events:
			self.add_schedule(event)

	def handle_right_click(self, date: QDate, pos: QPoint):
		# 找出触发右键的单元格
		clicked_item = None
		for item in self.scene.items():
			if isinstance(item, CalendarDayItem) and item.date == date:
				clicked_item = item
				break

		# 如果单元格未被选中，就单独选中它
		if clicked_item and not clicked_item._selected:
			self.clear_selection()
			clicked_item._selected = True
			clicked_item.update()

		# 收集当前所有选中项
		selected_items = [
			item for item in self.scene.items()
			if isinstance(item, CalendarDayItem) and item._selected
		]
		selected_dates = [item.date for item in selected_items]

		# 构造右键菜单
		menu = QMenu()
		if len(selected_dates) == 1:
			menu.addAction("查看当天日程", lambda: self.view_single_day.emit(date))
			# TODO:
			menu.addAction("删除该日全部事件", lambda: self.delete_events_for_day(selected_dates[0]))
		else:
			# TODO:
			menu.addAction(f"删除所选 {len(selected_dates)} 天事件", lambda: self.delete_multiple_days(selected_dates))

		menu.exec(pos)

	def refresh(self):
		log.info("刷新日历页面")
		self.handle_page_changed(self.current_year, self.current_month)
		self.draw_month(self.current_year, self.current_month)
		self.update_title()
