from operator import truediv

from common import *
from Emitter import Emitter
from functools import partial
from Event import BaseEvent, DDLEvent
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
				background-color: rgba(7, 193, 96, 0.1); /* 浅绿色背景 */
			}
			QPushButton:pressed {
				color: #05974C;
				background-color: rgba(5, 151, 76, 0.2); /* 按压加深 */
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
				background-color: rgba(7, 193, 96, 0.1);  /* 半透明绿色背景 */
				border: 1px solid rgba(7, 193, 96, 0.3);
				border-radius: 24px;                       /* 圆形 */
				min-width: 48px;
				min-height: 48px;
				padding: 0;
				color: #07C160;
				font-size: 24px;
				font-weight: 500;
				text-align: center;				
			}
			QPushButton:hover {
				background-color: rgba(7, 193, 96, 0.15);
				border: 1px solid rgba(7, 193, 96, 0.5);
				color: #05974C;
				font-size: 26px;                         /* 轻微放大 */
			}
			QPushButton:pressed {
				background-color: rgba(5, 151, 76, 0.2);
				border: 1px solid rgba(5, 151, 76, 0.7);
				color: #047245;
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
	delete_me_signal: Signal = Signal(DDLEvent)
	finished_signal: Signal = Signal(DDLEvent)
	unfinished_signal: Signal = Signal(DDLEvent)
	view_and_edit_signal: Signal = Signal(DDLEvent)

	def __init__(self, event: DDLEvent, parent=None):
		super().__init__(parent)
		self.setAttribute(Qt.WA_StyledBackground, True)
		# 绑定item和对应的event
		self.nevent = event

		# 设置消息布局
		layout = QHBoxLayout(self)
		layout.setContentsMargins(5, 2, 5, 2)  # 边距：左、上、右、下
		self.setStyleSheet("""CustomListItem {background-color: palette(light);border-radius: 15px;}
				CustomListItem:hover {background-color: palette(midlight); /*轻微高亮*/}""")

		# 是否完成的复选框
		self.finish_checkbox = QCheckBox()
		if event.done == 1:
			self.finish_checkbox.setChecked(True)  # 设置为选中状态

		# 当打勾时触发
		self.finish_checkbox.clicked.connect(lambda checked: self.this_one_is_finished() if checked else None)
		# 当取消打勾时触发
		self.finish_checkbox.clicked.connect(lambda checked: self.make_this_one_unfinished() if not checked else None)
		layout.addWidget(self.finish_checkbox)

		# 展示主题的标签
		self.theme_display_label = QLabel(f"{event.title}")
		if event.done == 0:
			set_font(self.theme_display_label)
		else:
			set_font(self.theme_display_label, 3)
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

	def this_one_is_finished(self):
		"""标记日程已完成"""
		self.finished_signal.emit(self.nevent)

	def make_this_one_unfinished(self):
		self.unfinished_signal.emit(self.nevent)


class Record:
	"""记录放到Upcoming里的日程"""
	#TODO：现在没用
	def __init__(self, id, pos, date, finished):
		self.id = id
		self.pos = pos  # 在Upcoming里的位置
		self.date = date  # 格式："yyyy-MM-dd HH:mm"
		self.finished = finished  # 是否完成

	def __lt__(self, other):
		if self.finished:
			if other.finished:
				return self.date < other.date
			else:
				return False
		else:
			if other.finished:
				return True
			else:
				return self.date < other.date


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
			""")

		self.kind = kind  # 0:Upcoming页面的Upcoming；1:Calendar页面的search_column；2:某个日期的Upcoming
		self.events_used_to_update: tuple[DDLEvent] = tuple()  # 储存这次需要更新的至多10个数据
		self.index_of_date_label = dict()  # 储存显示日期的项的位置
		self.items_of_one_date = dict()  # 储存同一日期的项的位置,每个日期对应一个列表，列表中的项为tuple(id,位置)
		self.loading = False  # 是否正在加载
		self.no_more_events = False  # 是否显示全部数据
		self.event_num = 0  # 记录当前个数，传给后端提取数据
		self.page_num = 10  # 每页显示的事件数
		self.loading_item = None  # 加载标签

		# MainWindow的search_column不用预先加载
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
			date_item = QListWidgetItem('\n今天\n————————')
		elif date == tomorrow:
			date_item = QListWidgetItem('\n明天\n————————')
		else:
			tmp_date = date.split('-')
			if date[:4] == today[:4]:
				date_item = QListWidgetItem(f"\n{int(tmp_date[1])}月{int(tmp_date[2])}日\n————————")
			else:
				date_item = QListWidgetItem(f"\n{tmp_date[0]}年{int(tmp_date[1])}月{int(tmp_date[2])}日\n————————")
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

	def get_data(self, data: tuple[BaseEvent] = None):
		"""从后端加载数据"""
		if data is not None and len(data) > 0:
			log.info(f"接收数据成功，共接收 {len(data)} 条数据：\n" +
					 "\n".join(f"- {event.title} @ {event.datetime}" for event in data))
			self.events_used_to_update = data
			self.event_num += len(data)
		# if len(data) < self.page_num:#TODO：应对奇怪的问题
		#	self.no_more_events = True
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
		custom_widget = CustomListItem(event)
		item = QListWidgetItem()
		item.setSizeHint(QSize(custom_widget.sizeHint().width(), 80))  # 设置合适的大小
		# 如果没有对应日期的标签，就加上
		if not event.datetime[:10] in self.index_of_date_label:
			self.add_date_label(event.datetime)
			# 如果未完成，插到自己的日期标签的下方
			if event.done == 0:
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
			if event.done == 0:
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
		log.info(f"查看编辑事件：{event.title}; 提醒时间：{event.advance_time}")
		Emitter.instance().send_view_and_edit_schedule_signal((event,))

	def finish_one_item(self, event: BaseEvent):
		"""标记一个事件已完成"""
		# 先删除
		self.delete_one_item(event, True)
		# TODO:通知后端;再次刷新时保持这一状态
		event.done = 1
		# 再插入
		self.add_one_item(event)
		log.info(f"标记该事件完成：{event.title} @ {event.datetime}")

	def make_one_item_unfinished(self, event: BaseEvent):
		"""取消复选框的对勾"""
		# TODO：通知后端;再次刷新时保持这一状态
		self.delete_one_item(event, True)
		# 再获取“是否完成”改变后的event
		event.done = 0
		# 再插入
		self.add_one_item(event)
		log.info(f"标记该事件未完成：{event.title} @ {event.datetime}")

	def delete_one_item(self, event: BaseEvent, keep_corresponding_event=False):
		"""
		删除事件
		:param keep_corresponding_event: 复选框变化时也要调用，当其为True时，不从后端删除
		"""
		date = event.datetime[:10]
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
		elif self.kind == 2:
			# TODO:只获取指定日期的待办
			pass

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
		self.load_more_data()
		log.info(f"共{self.event_num}条日程")
