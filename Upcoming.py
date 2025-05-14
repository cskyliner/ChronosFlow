from common import *
from Emitter import Emitter
from functools import partial
from Event import BaseEvent, DDLEvent

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
				border-radius: 8px;                       /* 圆角 */
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

	def __init__(self, theme, parent=None):
		super().__init__(parent)
		self.setAttribute(Qt.WA_StyledBackground, True)

		self.setStyleSheet("""
		            CustomListItem {
		                background-color: transparent;
		                border-radius: 4px;
		            }
		            CustomListItem:hover {
		                background-color: palette(midlight); /*轻微高亮*/
		            }
		        """)

		# 设置消息布局
		layout = QHBoxLayout(self)
		layout.setContentsMargins(5, 2, 5, 2)  # 边距：左、上、右、下

		# 是否完成的复选框
		self.finish_checkbox = QCheckBox()
		self.finish_checkbox.toggled.connect(partial(self.this_one_is_finished))
		layout.addWidget(self.finish_checkbox)

		# 字体
		font = QFont()
		font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
		font.setPointSize(13)
		font1 = QFont()  # 用于‘+’的字体
		font1.setPointSize(18)

		# 展示主题的标签
		self.theme_display_label = QLabel(f"{theme}")
		self.theme_display_label.setFont(font)
		layout.addWidget(self.theme_display_label)

		# 弹性空白区域（将右侧按钮推到最右）
		spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
		layout.addItem(spacer)

		self.view_schedule_button = EyeButton()
		# self.view_schedule_button.clicked.connect() TODO: 跳转到之前的日程记录页面,需要补充函数访问后端数据
		# self.delete_button.clicked.connect() TODO: 需要补充函数删除这个日程对应的后端数据(前端消失我之后再写)
		self.delete_button = DeleteButton()

		self.setLayout(layout)
		layout.addWidget(self.view_schedule_button)
		layout.addWidget(self.delete_button)

	def this_one_is_finished(self):
		"""打勾后发信号"""
		# TODO
		pass



class Upcoming(QListWidget):
	"""
	容纳多个SingleUpcoming，有滚动等功能
	"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setDragDropMode(QListWidget.InternalMove)  # 允许内部拖动重排
		self.setDefaultDropAction(Qt.MoveAction)  # 设置默认动作为移动而非复制
		self.setSelectionMode(QListWidget.SingleSelection)  # 一次只能选择列表中的一个项目
		self.model().rowsMoved.connect(self.show_current_order_to_backend)  # 将顺序改变加入日志，并通知后端

		palette = self.palette()
		self.setStyleSheet(f"""
		    QListWidget::item:selected {{
		        background: transparent;
		        color: {palette.text().color().name()};
		        border: none;
		    }}
		""")

		self.events: list[DDLEvent] = []  # 存贮所有从后端得到的数据，用于储存id
		self.events_used_to_update: tuple[DDLEvent] = tuple()  # 储存这次需要更新的至多10个数据
		self.index_of_data_label = dict()  # 储存显示日期的项的位置
		self.loading = False  # 是否正在加载
		self.no_more_events = False  # 是否显示全部数据
		self.event_num = 0  # 记录当前个数，传给后端提取数据
		self.page_num = 10  # 每页显示的事件数
		self.loading_item = None  # 加载标签

		# 添加今天、明天两个标签
		font = QFont()
		font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
		font.setPointSize(12)
		today = QDate.currentDate()
		tomorrow = today.addDays(1)
		today_date_item = QListWidgetItem("今天")
		tomorrow_date_item = QListWidgetItem("\n明天")
		today_date_item.setFont(font)
		self.addItem(today_date_item)
		tomorrow_date_item.setFont(font)
		self.addItem(tomorrow_date_item)
		self.index_of_data_label[today.toString("yyyy-MM-dd")] = QPersistentModelIndex(
			self.indexFromItem(today_date_item))
		self.index_of_data_label[tomorrow.toString("yyyy-MM-dd")] = QPersistentModelIndex(
			self.indexFromItem(tomorrow_date_item))

		self.load_more_data()
		self.verticalScrollBar().valueChanged.connect(self.check_scroll)  # 检测是否滚动到底部
		log.info(f"共{self.event_num }条日程")

		#Emitter.instance().refresh_upcoming_signal.connect(self.refresh_upcoming_page)
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

	def show_current_order_to_backend(self):
		"""在Upcoming中顺序改变时显示在log中，并通知后端"""
		# TODO：通知后端：移动的event的日期改变
		log.info("Upcoming顺序改变")

	def show_loading_label(self):
		self.loading_item = QListWidgetItem("Loading……")
		self.loading_item.setTextAlignment(Qt.AlignCenter)
		self.addItem(self.loading_item)

	def add_date_label(self, date):
		"""
		在所有同一天的日程前加上日期
		仅支持python3.7及以上
		"""
		font = QFont()
		font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
		font.setPointSize(12)
		date = date[:10]
		tmp_date = date.split('-')
		date_item = QListWidgetItem(f"\n{tmp_date[0]}年{int(tmp_date[1])}月{int(tmp_date[2])}日")
		date_item.setFont(font)
		# 寻找插入位置（第一个比自身日期大的日期）
		find = False
		for key in self.index_of_data_label.keys():
			if key > date:
				find = True
				record = key
				break
		if find:
			self.insertItem(self.index_of_data_label[record].row(), date_item)
		else:
			self.addItem(date_item)
		self.index_of_data_label[date] = QPersistentModelIndex(self.indexFromItem(date_item))
		self.index_of_data_label = dict(sorted(self.index_of_data_label.items()))  # 保证日期标签按升序排列，仅支持python3.7及以上

	def get_data(self, data: tuple[DDLEvent] = None):
		"""从后端加载数据"""
		if data is not None and len(data) > 0:
			log.info(f"接收数据成功，共接收 {len(data)} 条数据：\n" +
					 "\n".join(f"- {event.title} @ {event.datetime}" for event in data))
			self.events.extend(data)
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

	def add_one_item(self, event):
		"""
		将每条的日期和已有的日期比较，如果日期已有，插入到这一日期标签的下面；如果没有，新建日期标签
		self.index_of_data_label的形式为event.datetime[:10],仅有年月日
		"""
		custom_widget = CustomListItem(f"{event.title}")
		item = QListWidgetItem()
		item.setSizeHint(QSize(custom_widget.sizeHint().width(), 80))  # 设置合适的大小
		# 如果没有对应日期的标签，就加上
		if not event.datetime[:10] in self.index_of_data_label:
			self.add_date_label(event.datetime)

		self.insertItem(self.index_of_data_label[event.datetime[:10]].row() + 1, item)
		self.setItemWidget(item, custom_widget)

	def load_more_data(self):
		"""将数据添加到self"""
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
