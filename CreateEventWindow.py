from common import *
from Emitter import Emitter
from FontSetting import set_font

log = logging.getLogger(__name__)


class StrictDynamicLineEdit(QLineEdit):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._parent = parent
		self.update_limits()

		# 禁止影响父控件布局
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

		# 设置占位提示文字
		self.setPlaceholderText("标题")
		set_font(self)

		# 初始宽度
		self.setFixedWidth(self._min_width)
		self.setFixedHeight(50)

		self.setStyleSheet("""QLineEdit {
			background-color: rgba(255, 255, 255, 0.4);  /* 亮色主题半透明 */
		    color: palette(text);  /* 使用系统文本颜色 */
			border: none;
			border-bottom: 1px solid palette(shadow);
		}""")

		# 监听文本变化
		self.textChanged.connect(self.adjust_width)

	def update_limits(self):
		"""从父控件获取当前允许的宽度范围"""
		if self._parent:
			self._min_width = int(self._parent.width() * 0.4)
			self._max_width = self._parent.width()

	def adjust_width(self):
		"""根据内容调整宽度，限制在父控件范围内"""
		# 确保使用最新的宽度限制
		self.update_limits()

		# 计算文本实际需要的宽度（包括边距）
		text_width = self.fontMetrics().boundingRect(self.text()).width() + 20

		# 严格限制宽度范围
		new_width = max(self._min_width, min(text_width, self._max_width))

		# 关键点：先解除固定宽度限制，再设置新宽度
		self.setMinimumWidth(0)
		self.setMaximumWidth(self._max_width)
		self.setFixedWidth(new_width)

	def resizeEvent(self, event):
		"""父控件大小改变时重新调整"""
		self.update_limits()
		self.adjust_width()
		super().resizeEvent(event)


class ContainerFrame(QFrame):
	"""隔离层，确保布局变化不会传递到主窗口"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setFixedHeight(50)
		self.setFrameShape(QFrame.NoFrame)
		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)

		# 添加动态文本框
		self.line_edit = StrictDynamicLineEdit(self)
		layout.addWidget(self.line_edit, 0, Qt.AlignLeft)

		# 添加伸缩项固定布局
		layout.addStretch()

	def text(self):
		return self.line_edit.text()

	def clear(self):
		self.line_edit.clear()

	def setText(self,content):
		self.line_edit.setText(content)


class Schedule(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.standard_date = None
		self.date = ['0000', '00', '00']  # 日期
		self.datetime = ['00', '00']  # TODO:调整具体时间（小时，分钟）
		layout = QVBoxLayout(self)
		layout.setSpacing(0)

		# 创建框
		self.group_box = QGroupBox("添加日程")
		self.group_box.setStyleSheet("""
    		QGroupBox {
                border: 1px solid palette(mid);
                border-radius: 10px;
                margin-top: 1.5ex;
                padding: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
		set_font(self.group_box)

		group_layout = QVBoxLayout()

		# 动态调整宽度的主题文本框
		self.theme_text_edit = ContainerFrame(self)
		group_layout.addWidget(self.theme_text_edit)

		# 创建多行文本框
		self.text_edit = QPlainTextEdit()
		self.text_edit.setPlaceholderText("内容")
		# 设置半透明和自适应主题的样式表
		self.text_edit.setStyleSheet("""
		    QPlainTextEdit {
		        background-color: rgba(255, 255, 255, 0.4);  /* 亮色主题半透明 */
		        color: palette(text);  /* 使用系统文本颜色 */
		        border: 1px solid palette(shadow);
		        border-radius: 4px;
		    }
		    QScrollBar:vertical {
		        background: transparent;
		        width: 8px;
		    }
		    QScrollBar::handle:vertical {
		        background: palette(mid);
		        min-height: 20px;
		        border-radius: 4px;
		    }
		""")
		set_font(self.text_edit)
		group_layout.addWidget(self.text_edit)

		self.group_box.setLayout(group_layout)
		layout.addWidget(self.group_box)

		# 截止、提醒时间选择框
		deadline_and_reminder_label_layout = QHBoxLayout()
		layout.addLayout(deadline_and_reminder_label_layout)
		# 截止时间选择框
		deadline_layout = QVBoxLayout()
		self.deadline_label = QLabel("截止时间:")
		set_font(self.deadline_label)
		deadline_layout.addWidget(self.deadline_label)

		self.deadline_edit = QDateTimeEdit()
		set_font(self.deadline_edit)
		self.deadline_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
		self.deadline_edit.setDateTime(QDateTime.currentDateTime())
		self.deadline_edit.setCalendarPopup(True)  # 在点击时弹出日历
		calendar = self.deadline_edit.calendarWidget()  # 获取日历控件（QCalendarWidget）
		calendar.setStyleSheet("""
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
					""")  # 设置日历样式
		deadline_layout.addWidget(self.deadline_edit)
		deadline_and_reminder_label_layout.addLayout(deadline_layout)

		# 提醒时间选择框
		reminder_layout = QVBoxLayout()
		self.reminder_label = QLabel("提醒时间:")
		set_font(self.reminder_label)
		reminder_layout.addWidget(self.reminder_label)

		self.reminder_edit = QDateTimeEdit()
		set_font(self.reminder_edit)
		self.reminder_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
		self.reminder_edit.setDateTime(QDateTime.currentDateTime())
		self.reminder_edit.setCalendarPopup(True)
		calendar = self.reminder_edit.calendarWidget()  # 获取日历控件（QCalendarWidget）
		calendar.setStyleSheet("""
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
				    """)  # 设置日历样式
		reminder_layout.addWidget(self.reminder_edit)
		deadline_and_reminder_label_layout.addLayout(reminder_layout)

		# 创建按钮
		button_layout = QHBoxLayout()
		layout.addLayout(button_layout)

		self.save_btn = QPushButton("保存")
		self.save_btn.clicked.connect(self.create_new_event)
		self.save_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.4);
                    border: 1px solid palette(mid);
                	border-radius: 4px;
                    padding: 25px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.6); /*轻微高亮*/
                    border-radius: 4px;
                }
                QPushButton:pressed {
					background-color: rgba(255, 255, 255, 0.8);
				}
							""")
		set_font(self.save_btn)
		button_layout.addWidget(self.save_btn)

		# 状态栏
		self.status_label = QLabel()
		layout.addWidget(self.status_label)

		# 如果用于修改事件，储存事件ID
		self.id = None

	def receive_date(self, date: QDate):
		"""
		接收date，并进行格式转化
		"""
		# 为了方便后面数据进行储存，这里转换过程中间储存了QDate格式，但在GUI界面的显示方式仍为年月日
		self.standard_date = date
		self.date = self.standard_date.toString("yyyy-MM-dd").split('-')
		log.info(f"收到日期信息：{self.date[0]}年{self.date[1]}月{self.date[2]}日")
		self.deadline_edit.setDate(QDate(int(self.date[0]), int(self.date[1]), int(self.date[2])))
		self.reminder_edit.setDate(QDate(int(self.date[0]), int(self.date[1]), int(self.date[2])))

	def create_new_event(self):
		"""
		保存内容，暂时后端只做了DDL类 TODO:支持不同形式event的储存
		传送内容为event类别（DDL），该类别所需参数
		TODO:向Notice的schedule_notice发信号，重要程度的选择
		"""
		theme = self.theme_text_edit.text()
		content = self.text_edit.toPlainText()
		deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		reminder = self.reminder_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		notify_time = self.reminder_edit.dateTime()
		log.info(f"notify_time是{notify_time}")
		"""
		time = QTime(int(self.datetime[0]), int(self.datetime[1]))
		datetime = QDateTime(self.standard_date, time)
		datetime_str = datetime.toString("yyyy-MM-dd HH:mm")
		test_advance_time = datetime.addDays(-1)
		test_advance_time_str = test_advance_time.toString("yyyy-MM-dd HH:mm")
  		"""
		if theme and content and deadline and reminder:
			if self.id is None:
				# 新建事件
				log.info(
					f"创建新事件，标题：{theme}, 截止时间：{deadline}, 内容：{content}, 提前提醒时间：{reminder}, 重要程度：Great"),
				# DDL参数(标题，截止时间，具体内容，提前提醒时间，重要程度)
				Emitter.instance().send_create_event_signal("DDL", theme, deadline, content, reminder, "Great")
				QMessageBox.information(self, "保存成功",
										f"主题: {theme}\n内容: {content}\n截止时间: {deadline}\n提醒时间: {reminder}")
			else:
				log.info(
				f"修改事件，事件ID: {self.id} 标题：{theme}, 截止时间：{deadline}, 内容：{content}, 提前提醒时间：{reminder}, 重要程度：Great"),
				# DDL参数(标题，截止时间，具体内容，提前提醒时间，重要程度)
				Emitter.instance().send_modify_event_signal(self.id, "DDL", theme, deadline, content, reminder, "Great")
				QMessageBox.information(self, f"修改事件{self.id}成功",
										f"主题: {theme}\n内容: {content}\n截止时间: {deadline}\n提醒时间: {reminder}")
				self.id = None
		else:
			QMessageBox.warning(self, "警告", "请填写所有信息")

	def get_selected_times(self):
		"""返回用户选择的截止时间和提醒时间"""
		deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		reminder = self.reminder_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		return deadline, reminder
