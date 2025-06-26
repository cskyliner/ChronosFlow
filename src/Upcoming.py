from common import *
from Emitter import Emitter
from events.Event import *
from FontSetting import set_font

log = logging.getLogger("Upcoming")


class DeleteButton(QPushButton):
	def __init__(self, parent=None):
		super().__init__("🗑", parent)  # 使用垃圾桶emoji
		self.setStyleSheet("""
			QPushButton {
				background-color: rgba(255, 80, 80, 0.1);  /* 半透明红色背景 */
				border: 1px solid rgba(255, 80, 80, 0.3);
				border-radius: 8px;
				min-width: 48px;
				min-height: 48px;
				padding: 0;
				padding-top: -6px;  /* 关键对齐参数 */
				color: #FF5050;
				font-size: 24px;
				font-weight: 500;
				text-align: center;
			}
			QPushButton:hover {
				background-color: rgba(255, 80, 80, 0.15);
				border: 1px solid rgba(255, 80, 80, 0.5);
				color: #E03C3C;
				font-size: 26px;
			}
			QPushButton:pressed {
				background-color: rgba(224, 60, 60, 0.2);
				border: 1px solid rgba(224, 60, 60, 0.7);
				color: #C03030;
				padding-top: 2px;
			}
		""")

		self.setToolTip("删除")
		self.setCursor(Qt.PointingHandCursor)
		self.setFixedSize(40, 40)

		# 红色阴影效果
		shadow = QGraphicsDropShadowEffect()
		shadow.setBlurRadius(8)
		shadow.setColor(QColor(255, 80, 80, 60))
		shadow.setOffset(0, 2)
		self.setGraphicsEffect(shadow)

	def bind_event(self, event: BaseEvent):
		self._event = event


class EyeButton(QPushButton):
	"""单例眼睛按钮"""
	_instance = None

	@staticmethod
	def instance() -> "EyeButton":
		if EyeButton._instance is None:
			EyeButton._instance = EyeButton()
		return EyeButton._instance

	def __init__(self, parent=None):
		super().__init__("👁️", parent)
		self.setStyleSheet("""
			QPushButton {
				background-color: transparent;
				border: none;
				padding: 10px 15px;  /* 更紧凑的点击区域 */
				font-size: 24px;     /* 放大图标 */
				qproperty-iconSize: 24px;  /* 如果使用 setIcon() */
				color: #555;        /* 中性灰色 */
				border-radius: 4px; /* 圆角悬停背景 */
			}
			QPushButton:hover {
				color: #07C160;     /* 绿色悬停 */
				background-color: rgba(7, 193, 96, 0.2); /* 浅绿色背景 */
			}
			QPushButton:pressed {
				color: #05974C;
				background-color: rgba(5, 151, 76, 0.4); /* 按压加深 */
			}
		""")
		self.setToolTip("查看")  # 增加提示文本
		self.setCursor(Qt.PointingHandCursor)  # 手型光标


class FloatingButton(QPushButton):
	"""悬浮按钮"""

	def __init__(self, parent=None):
		super().__init__("+", parent)
		self.setStyleSheet("""
			QPushButton {
				background-color: rgba(30, 144, 255, 0.6);  /* 半透明绿色背景 */
				border: 1px solid rgba(30, 112, 255, 0.6);
				border-radius: 24px;                       /* 圆形 */
				min-width: 48px;
				min-height: 48px;
				padding: 0;
				color: white;
				font-size: 24px;
				font-weight: 500;
				text-align: center;				
			}
			QPushButton:hover {
				background-color: rgba(30, 144, 255, 0.8);
				border: 1px solid rgba(30, 112, 255, 0.8);
				color: white;
				font-size: 26px;                         /* 轻微放大 */
			}
			QPushButton:pressed {
				background-color: rgba(30, 144, 255, 0.9);
				border: 1px solid rgba(30, 112, 255, 0.9);
				color: white;
				padding-top: 2px;                        /* 按压下沉效果 */
			}
		""")
		self.setToolTip("添加")
		self.setCursor(Qt.PointingHandCursor)
		self.setFixedSize(40, 40)  # 放大按钮本身
		# 添加图标动画效果
		self.setGraphicsEffect(
			QGraphicsDropShadowEffect(blurRadius=8, color=QColor(7, 193, 96, 60), offset=QPointF(0, 2)))

		# 设置相对位置参数（百分比或固定偏移量）
		self.relative_position = (0.94, 0.9)  # (水平位置比例, 垂直位置比例)
		# 监听父控件resize事件
		if parent:
			parent.installEventFilter(self)

	def update_position(self):
		"""根据父控件大小更新位置"""
		if self.parent():
			parent_rect = self.parent().rect()
			x = int(parent_rect.width() * self.relative_position[0] - self.width())
			y = int(parent_rect.height() * self.relative_position[1] - self.height())
			self.move(x, y)

	def eventFilter(self, obj, event):
		"""监听父控件resize事件"""
		if obj == self.parent() and event.type() == QEvent.Resize:
			self.update_position()
		return super().eventFilter(obj, event)

	def showEvent(self, event):
		"""初始显示时定位"""
		self.update_position()
		super().showEvent(event)


class CustomListItem(QWidget):
	"""一条日程"""
	delete_me_signal: Signal = Signal(BaseEvent)
	view_and_edit_signal: Signal = Signal(BaseEvent)
	finished_signal: Signal = Signal(BaseEvent)
	unfinished_signal: Signal = Signal(BaseEvent)

	def __init__(self, event: BaseEvent, parent=None, color_choice=0):
		super().__init__(parent)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setAutoFillBackground(False)
		self.setMouseTracking(True)  # 启用鼠标跟踪

		colors = (
			"rgba(210, 125, 150, 0.9)",
			"rgba(230, 205, 145, 0.9)",
			"rgba(140, 175, 195, 0.9)",
			"rgba(150, 165, 135, 0.9)",
			"rgba(225, 160, 125, 0.9)",
			"rgba(175, 155, 190, 0.9)"
		)
		self.setStyleSheet(f"""
		            CustomListItem {{
		                border-radius: 15px;
		                background-color: {colors[color_choice]};
		            }}
		            CustomListItem:hover {{
		                background-color: {colors[color_choice].replace('0.9', '1.0')};
		            }}
		        """)

		# 绑定item和对应的event
		self.nevent = event

		# 设置消息布局
		layout = QHBoxLayout(self)
		layout.setContentsMargins(5, 2, 5, 2)  # 边距：左、上、右、下

		if hasattr(self.nevent, "done"):
			self.finish_checkbox = QCheckBox()
			self.finish_checkbox.setChecked(bool(self.nevent.done))
			# self.finish_checkbox.clicked.connect(lambda x:self.this_one_is_finished(x))
			# 当打勾时触发
			self.finish_checkbox.clicked.connect(lambda checked: self.make_this_one_finished() if checked else None)
			# 当取消打勾时触发
			self.finish_checkbox.clicked.connect(
				lambda checked: self.make_this_one_unfinished() if not checked else None)
			layout.addWidget(self.finish_checkbox)

		# 展示主题的标签
		self.theme_display_label = QLabel(f"{event.title}")
		self.theme_display_label.setStyleSheet("""
				color: palette(text);
		""")
		if hasattr(event, "done"):
			if event.done == 0:
				set_font(self.theme_display_label)
			else:
				set_font(self.theme_display_label, 3)
		else:
			set_font(self.theme_display_label)
		layout.addWidget(self.theme_display_label)

		# 弹性空白区域（将右侧按钮推到最右）
		spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
		layout.addItem(spacer)

		self.view_schedule_button = EyeButton()
		self.view_schedule_button.clicked.connect(self.this_one_is_viewed_and_edited)
		self.delete_button = DeleteButton()
		self.delete_button.clicked.connect(self.this_one_is_deleted)

		self.setLayout(layout)
		layout.addWidget(self.view_schedule_button)
		layout.addWidget(self.delete_button)

	def this_one_is_deleted(self):
		self.delete_me_signal.emit(self.nevent)

	def this_one_is_viewed_and_edited(self):
		"""查看后发信号"""
		self.view_and_edit_signal.emit(self.nevent)

	# def this_one_is_finished(self, checked: bool):
	# 	"""打勾或取消打勾后发信号"""
	# 	self.nevent.done = checked
	# 	if isinstance(self.nevent, DDLEvent):
	# 		Emitter.instance().send_modify_event_signal(self.nevent.id, "DDL", *self.nevent.to_args())
	# 	else:
	# 		log.error(f"{type(self.nevent)}事件未实现完成功能")

	def make_this_one_finished(self):
		"""标记日程已完成"""
		self.nevent.done = 1
		if isinstance(self.nevent, DDLEvent):
			Emitter.instance().send_modify_event_signal(self.nevent.id, "DDL", *self.nevent.to_args())
		else:
			log.error(f"{type(self.nevent)}事件未实现完成功能")
		self.finished_signal.emit(self.nevent)

	def make_this_one_unfinished(self):
		self.nevent.done = 0
		if isinstance(self.nevent, DDLEvent):
			Emitter.instance().send_modify_event_signal(self.nevent.id, "DDL", *self.nevent.to_args())
		else:
			log.error(f"{type(self.nevent)}事件未实现完成功能")
		self.unfinished_signal.emit(self.nevent)


class Upcoming(QListWidget):
	"""
	容纳多个SingleUpcoming，有滚动等功能
	"""

	def __init__(self, kind=0, parent=None):
		super().__init__(parent)

		self.setStyleSheet("""
		    QListWidget::item:selected {
		        background: transparent;
		        border: none;
		        color: palette(text)
		    }
		    QListWidget { background: transparent; }
		    QListWidget::item {
        			/* 控制行间距（相邻项的间隔） */
        			margin: 5px;  
        	}
			/* 垂直滚动条 */
			QScrollBar:vertical {
				border: none;
				background: palette(base);
				width: 3px;
				margin: 0px 0px 0px 0px;
			}
			QScrollBar::handle:vertical {
				background: #1E90FF;
				min-height: 20px;
				border-radius: 6px;
			}
			QScrollBar::handle:vertical:hover {
				background: #1E90FF;
			}
			QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
				border: none;
				background: none;
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
			
			/* 水平滚动条 */
			QScrollBar:horizontal {
				border: none;
				background: palette(base);
				height: 3px;
				margin: 0px 0px 0px 0px;
			}
			QScrollBar::handle:horizontal {
				background: #1E90FF;
				min-width: 20px;
				border-radius: 6px;
			}
			QScrollBar::handle:horizontal:hover {
				background: #1E90FF;
			}
			QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
				border: none;
				background: none;
				width: 0px;
			}
			QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
				background: none;
			}
			QListWidget::item:selected {
				background: transparent;
				border: none;
				color: palette(text)
			}
			QListWidget { background: transparent; }
			QListWidget::item {
					/* 控制行间距（相邻项的间隔） */
					margin: 5px;  
			}
		""")

		self.kind = kind  # 0:Upcoming页面的Upcoming；1:Calendar页面的search_column；2:某个日期的Upcoming
		self.events_used_to_update: tuple[BaseEvent] = tuple()  # 储存这次需要更新的至多10个数据
		self.index_of_date_label = dict()  # 储存显示日期的项的位置
		self.items_of_one_date = dict()  # 储存同一日期的项的位置,每个日期对应一个列表，列表中的项为tuple(id,位置)
		self.loading = False  # 是否正在加载
		self.no_more_events = False  # 是否显示全部数据
		self.event_num = 0  # 记录当前个数，传给后端提取数据
		self.page_num = 10  # 每页显示的事件数
		self.loading_item = None  # 加载标签
		self.float_btn: FloatingButton = None  # 悬浮按钮
		self.color_choice = 0  # 0:red 1:yellow 2:blue 3:green

		if self.kind == 0:
			self.load_more_data()
			log.info(f"共{self.event_num}条日程")
			self.verticalScrollBar().valueChanged.connect(self.check_scroll)  # 检测是否滚动到底部
		elif self.kind == 2:
			self.load_more_data()

	def check_scroll(self):
		"""检查是否滚动到底部"""
		if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
			log.info("检查滚动!")
			if not self.loading and not self.no_more_events:
				self.load_more_data()
			elif self.loading:
				log.info("正在加载数据，请稍等……")
			elif self.no_more_events:
				log.info("没有更多数据了，停止加载……")
			else:
				log.error("未知错误，无法加载数据")

	def show_loading_label(self):
		"""显示加载标签"""
		self.loading_item = QListWidgetItem("Loading……")
		self.loading_item.setTextAlignment(Qt.AlignCenter)
		self.addItem(self.loading_item)

	def add_date_label(self, date):
		"""
		在所有同一天的日程前加上日期
		"""
		today = QDate.currentDate()
		tomorrow = today.addDays(1).toString("yyyy-MM-dd")
		today = today.toString("yyyy-MM-dd")

		date = date[:10]
		if date == today:
			date_text = '\n今天\n————————'
		elif date == tomorrow:
			date_text = '\n明天\n————————'
		else:
			tmp_date = date.split('-')
			if date[:4] == today[:4]:
				date_text = f"\n{int(tmp_date[1])}月{int(tmp_date[2])}日\n————————"
			else:
				date_text = f"\n{tmp_date[0]}年{int(tmp_date[1])}月{int(tmp_date[2])}日\n————————"

		date_item = QListWidgetItem(date_text)
		set_font(date_item)

		# 寻找插入位置（第一个比自身日期大的日期）
		record = None
		for key in self.index_of_date_label.keys():
			if key > date:
				record = key
				break
		if not record is None:
			self.insertItem(self.index_of_date_label[record].row(), date_item)
		else:
			self.addItem(date_item)
		self.index_of_date_label[date] = QPersistentModelIndex(self.indexFromItem(date_item))
		self.index_of_date_label = dict(sorted(self.index_of_date_label.items()))  # 保证日期标签按升序排列，仅支持python3.7及以上

	def get_specific_date_data(self, data: tuple[BaseEvent]):
		"""从后端加载特定日期的数据"""
		if data is not None and len(data) > 0:
			log.info(f"get_specific_date_data:接收数据成功，共接收 {len(data)} 条数据：\n" +
					 "\n".join(f"- {event.title} @ {event.datetime}" for event in data))
			self.events_used_to_update = data
			self.event_num += len(data)
		else:
			log.info("接受数据为空，无更多数据")
			# 数据加载完毕
			self.no_more_events = True

		# 删除加载标签
		if hasattr(self, "loading_item"):
			self.takeItem(self.row(self.loading_item))
			del self.loading_item
		self.index_of_date_label = dict(sorted(self.index_of_date_label.items()))  # 保证日期标签按升序排列

	def get_data(self, data: tuple[BaseEvent] = None):
		"""从后端加载数据"""
		if data is not None and len(data) > 0:
			log.info(f"接收数据成功，共接收 {len(data)} 条数据：\n" +
					 "\n".join(f"- {event.title} @ {event.datetime}" for event in data))
			self.events_used_to_update = data
			self.event_num += len(data)
		else:
			log.info("接受数据为空，无更多数据")
			# 数据加载完毕
			self.no_more_events = True
		# 删除加载标签
		if hasattr(self, "loading_item"):
			self.takeItem(self.row(self.loading_item))
			del self.loading_item

	def add_one_item(self, event: BaseEvent):
		"""
		将每条的日期和已有的日期比较，如果日期已有，插入到这一日期标签的下面；如果没有，新建日期标签
		self.index_of_data_label的key的形式为event.datetime[:10],仅有年月日
		"""
		custom_widget = CustomListItem(event, color_choice=self.color_choice)
		self.color_choice += 1
		if self.color_choice == 6:
			self.color_choice = 0

		item = QListWidgetItem()
		item.setSizeHint(QSize(custom_widget.sizeHint().width(), 80))  # 设置合适的大小

		# 如果没有对应日期的标签，就加上
		if not event.datetime[:10] in self.index_of_date_label:
			self.add_date_label(event.datetime)
			# 如果未完成，插到自己的日期标签的下方
			if hasattr(event, "done") and event.done == 0:
				self.insertItem(self.index_of_date_label[event.datetime[:10]].row() + 1, item)
				self.setItemWidget(item, custom_widget)
				self.items_of_one_date[event.datetime[:10]] = [
					(event.id, QPersistentModelIndex(self.indexFromItem(item)))]  # 获取永久位置
			# 如果完成，插到下一个日期标签的上方
			else:
				date = event.datetime[:10]
				record = None
				for key in self.index_of_date_label.keys():
					if key > date:
						record = key
						break
				if not record is None:
					self.insertItem(self.index_of_date_label[record].row(), item)
					self.setItemWidget(item, custom_widget)
					self.items_of_one_date[event.datetime[:10]] = [
						(event.id, QPersistentModelIndex(self.indexFromItem(item)))]
				else:
					self.addItem(item)
					self.setItemWidget(item, custom_widget)
					self.items_of_one_date[event.datetime[:10]] = [
						(event.id, QPersistentModelIndex(self.indexFromItem(item)))]
		else:
			if hasattr(event, "done") and event.done == 0:
				self.insertItem(self.index_of_date_label[event.datetime[:10]].row() + 1, item)
				self.setItemWidget(item, custom_widget)
				self.items_of_one_date[event.datetime[:10]].append(
					(event.id, QPersistentModelIndex(self.indexFromItem(item))))
			else:
				date = event.datetime[:10]
				record = None
				for key in self.index_of_date_label.keys():
					if key > date:
						record = key
						break
				if not record is None:
					self.insertItem(self.index_of_date_label[record].row(), item)
					self.setItemWidget(item, custom_widget)
					self.items_of_one_date[event.datetime[:10]].append(
						(event.id, QPersistentModelIndex(self.indexFromItem(item))))
				else:
					self.addItem(item)
					self.setItemWidget(item, custom_widget)
					self.items_of_one_date[event.datetime[:10]].append(
						(event.id, QPersistentModelIndex(self.indexFromItem(item))))

		custom_widget.delete_me_signal.connect(self.delete_one_item)
		custom_widget.view_and_edit_signal.connect(self.view_and_edit_one_item)
		custom_widget.finished_signal.connect(self.finish_one_item)
		custom_widget.unfinished_signal.connect(self.make_one_item_unfinished)
		log.info(f"{event.title}插入完成")

	def view_and_edit_one_item(self, event: BaseEvent):
		"""查看和编辑事件"""
		log.info(f"查看编辑事件：{event.title}")
		Emitter.instance().send_view_and_edit_schedule_signal((event,))

	def finish_one_item(self, event: BaseEvent):
		"""标记一个事件已完成"""
		# 先删除
		self.delete_one_item(event, True)
		# 再插入
		self.add_one_item(event)
		log.info(f"标记该事件完成：{event.title} @ {event.datetime}")

	def make_one_item_unfinished(self, event: BaseEvent):
		"""取消复选框的对勾"""
		self.delete_one_item(event, True)
		# 再插入
		self.add_one_item(event)
		log.info(f"标记该事件未完成：{event.title} @ {event.datetime}")

	def delete_one_item(self, event: BaseEvent, keep_corresponding_event=False):
		"""
		删除事件
		:param keep_corresponding_event: 复选框变化时也要调用，当其为True时，不从后端删除
		"""

		if isinstance(event, ActivityEvent) and event.datetime is None:
			log.info(f"ActivityEvent：{event.title} event.datetime:{event.datetime}")
			event.datetime = event.start_date + " " + event.start_time
			log.info(f"ActivityEvent：{event.title} event.datetime:{event.datetime}")
		elif isinstance(event, ActivityEvent):
			log.info(f"ActivityEvent：{event.title} event.datetime:{event.datetime}")
		# event.datetime = event.datetime
		date = event.datetime[:10]
		log.info(f"date = {date}")
		# 查找该事件
		for i in range(len(self.items_of_one_date[date])):
			if self.items_of_one_date[date][i][0] == event.id:
				self.takeItem(self.row(self.itemFromIndex(self.items_of_one_date[date][i][1])))  # 去除item
				self.event_num -= 1
				del self.items_of_one_date[date][i]
				if not keep_corresponding_event:
					log.info(f"删除事件成功：{event.title} @ {event.datetime}")
				# 删除日期标签
				if not keep_corresponding_event:
					if len(self.items_of_one_date[date]) == 0:
						del self.items_of_one_date[date]
						self.takeItem(self.row(self.itemFromIndex(self.index_of_date_label[date])))
						del self.index_of_date_label[date]
						log.info(f"日期标签删除成功：{date}")
				break
		if not keep_corresponding_event:
			Emitter.instance().send_delete_event_signal(event.id, event.table_name())

	def load_more_data(self):
		"""将数据添加到self"""
		if self.kind == 0:
			# 连接接收信号
			Emitter.instance().backend_data_to_frontend_signal.connect(self.get_data)
			# 显示加载标签
			self.show_loading_label()
			# 发送请求信号
			Emitter.instance().request_update_upcoming_event_signal(self.event_num, self.page_num)
			# 断开接收信号连接
			Emitter.instance().backend_data_to_frontend_signal.disconnect(self.get_data)
			# 停止加载
			self.loading = False
			if self.no_more_events:
				log.info("没有更多数据了，停止加载……")
				return
			for event in self.events_used_to_update:
				self.add_one_item(event)

	def load_searched_data(self, text):
		"""search_column"""
		if self.kind != 1:  # 仅供search_column调用
			log.error("load_searched_data被非search_column调用！")
			return

		self.clear()
		self.index_of_date_label.clear()
		self.items_of_one_date.clear()
		self.events_used_to_update = tuple()
		self.no_more_events = False
		self.loading = False
		self.event_num = 0
		self.loading_item = None
		self.color_choice = 0
		log.info(f"共{self.event_num}条日程")
		# 连接接收信号
		Emitter.instance().backend_data_to_frontend_signal.connect(self.get_data)
		# 显示加载标签
		self.show_loading_label()
		# 发送搜索信息
		Emitter.instance().request_search_all_event_signal(text)
		# 断开接收信号连接
		Emitter.instance().backend_data_to_frontend_signal.disconnect(self.get_data)

		if not self.no_more_events:
			for event in self.events_used_to_update:
				self.add_one_item(event)
		else:
			item = QListWidgetItem("没有匹配的日程")
			set_font(item)
			item.setTextAlignment(Qt.AlignCenter)
			self.addItem(item)

	def show_specific_date(self, date: QDate):
		"""显示指定日期的日程"""
		self.clear()
		self.index_of_date_label.clear()
		self.items_of_one_date.clear()
		self.events_used_to_update = tuple()
		self.loading = False
		self.no_more_events = False
		self.event_num = 0
		self.color_choice = 0
		self.loading_item = None
		# 连接接收信号
		Emitter.instance().backend_data_to_frontend_signal.connect(self.get_specific_date_data)
		# 显示加载标签
		self.show_loading_label()
		# 发送请求信号
		Emitter.instance().request_update_specific_date_upcoming_event_signal(date)
		# 断开接收信号连接
		Emitter.instance().backend_data_to_frontend_signal.disconnect(self.get_specific_date_data)
		# 停止加载
		self.loading = False
		if self.no_more_events:
			log.info("show_specific_date:没有更多数据了，停止加载……")
			self.notify_no_events()
			return
		for event in self.events_used_to_update:
			self.add_one_item(event)
		self.no_more_events = True

	def refresh_upcoming(self):
		"""用于每次切换到Upcoming时刷新"""
		if self.kind != 0:  # 仅限Upcoming页面使用
			log.error("refresh_upcoming被非Upcoming页面调用！")
			return

		self.clear()
		self.index_of_date_label.clear()
		self.items_of_one_date.clear()
		self.events_used_to_update = tuple()
		self.loading = False
		self.no_more_events = False
		self.event_num = 0
		self.loading_item = None
		self.color_choice = 0
		self.load_more_data()
		log.info(f"共{self.event_num}条日程")

	def notify_no_events(self):
		# 创建自定义样式的提示项
		# 创建提示项
		self.notify_item = QListWidgetItem()
		self.notify_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 文字居中

		# 使用Unicode符号+多行文本
		notice_text = """📅 当前没有日程安排
		────────────────
		✨ 点击下方 + 号添加首个日程"""

		# 设置字体样式
		set_font(self.notify_item, 4)

		# 设置文字颜色（使用QColor）
		self.notify_item.setForeground(QColor("#6c757d"))  # 中性灰文字

		# 交互限制
		self.notify_item.setFlags(Qt.ItemFlag.NoItemFlags)  # 禁止交互
		self.notify_item.setSizeHint(QSize(200, 100))  # 合适的高度
		self.notify_item.setText(notice_text)

		self.addItem(self.notify_item)
