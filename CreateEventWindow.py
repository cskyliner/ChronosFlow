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
			background-color: rgba(255, 255, 255, 0.6); 
		    color: black; 
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

	def setText(self, content):
		self.line_edit.setText(content)


class Schedule(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.standard_date = None
		self.date = ['0000', '00', '00']  # 日期
		self.datetime = ['00', '00']  # 调整具体时间（小时，分钟）
		layout = QVBoxLayout(self)
		layout.setSpacing(5)

		# 创建框
		self.group_box = QGroupBox("添加DDL")
		self.group_box.setStyleSheet("""
    		QGroupBox {
                border: 1px solid palette(text);
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
		self.text_edit = QTextEdit()
		self.text_edit.setPlaceholderText("内容")
		# 设置半透明和自适应主题的样式表
		self.text_edit.setStyleSheet("""
		    QTextEdit {
		        background-color: rgba(255, 255, 255, 0.6); 
		        color: black;  
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

		# 存储两种类型的对应选项
		two_types_layout = QVBoxLayout()
		layout.addLayout(two_types_layout)
		# 类型选择框(DDL,日程)
		type_choose_layout = QHBoxLayout()
		two_types_layout.addLayout(type_choose_layout)

		type_label = QLabel("类型：")
		set_font(type_label)
		type_choose_layout.addWidget(type_label)

		self.type_choose_combo = QComboBox()
		self.type_choose_combo.addItems(("DDL", "日程"))
		self.type_choose_combo.currentTextChanged.connect(self.update_dynamic_widgets)  # 信号
		type_choose_layout.addWidget(self.type_choose_combo)

		type_choose_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

		# 根据类型动态调整
		self.dynamic_widget_container = QWidget()
		self.dynamic_layout = QHBoxLayout(self.dynamic_widget_container)
		self.dynamic_layout.setSpacing(0)
		layout.addWidget(self.dynamic_widget_container)

		# 存储所有动态创建的部件
		self.ddl_widgets = self.create_ddl_widgets()
		self.schedule_widgets = self.create_schedule_widgets()
		#将汉语转为英语
		self.chinese_to_english = {'周一': 'Mon', '周二': 'Tue', '周三': 'Wed', '周四': 'Thu',
								   '周五': 'Fri', '周六': 'Sat', '周日': 'Sun'}
		# 连接信号槽
		self.type_choose_combo.currentTextChanged.connect(self.update_dynamic_widgets)

		# 初始显示ddl
		self.update_dynamic_widgets("DDL")

		# 创建保存按钮
		button_layout = QHBoxLayout()
		layout.addLayout(button_layout)

		self.save_btn = QPushButton("保存")
		self.save_btn.clicked.connect(self.create_new_event)
		self.save_btn.setMaximumHeight(100)
		self.save_btn.setMaximumWidth(200)
		self.save_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.6);
                    border: 1px solid palette(mid);
                    color: black;
                	border-radius: 4px;
                    padding: 10px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.8); /*轻微高亮*/
                    border-radius: 4px;
                }
                QPushButton:pressed {
					background-color: rgba(255, 255, 255, 0.9);
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
		向Notice的schedule_notice发信号，重要程度的选择
		"""
		_type = self.type_choose_combo.currentText()
		theme = self.theme_text_edit.text()
		content = self.text_edit.toPlainText()

		#time = QTime(int(self.datetime[0]), int(self.datetime[1]))
		#datetime = QDateTime(self.standard_date, time)
		#datetime_str = datetime.toString("yyyy-MM-dd HH:mm")
		#test_advance_time = datetime.addDays(-1)
		#test_advance_time_str = test_advance_time.toString("yyyy-MM-dd HH:mm")

		if theme:  # 可以支持只有主题，没有内容，多行文本框会返回空字符串，没有问题
			if _type == "DDL":
				self.theme_text_edit.clear()
				self.text_edit.clear()
				deadline_dt = self.deadline_edit.dateTime()
				reminder_dt = self.reminder_edit.dateTime()

				if deadline_dt < reminder_dt:
					QMessageBox.warning(self, "时间错误", "截止时间不能早于提醒时间！")
					return
				deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
				reminder = self.reminder_edit.dateTime().toString("yyyy-MM-dd HH:mm")
				log.info(f"notify_time是{self.reminder_edit.dateTime()}")
				if deadline and reminder:
					if self.id is None:
						# 新建事件
						log.info(
							f"创建新{_type}事件，标题：{theme}, 截止时间：{deadline}, 内容：{content}, 提前提醒时间：{reminder}, 重要程度：Great")
						# DDL参数(标题，截止时间，具体内容，提前提醒时间，重要程度)
						Emitter.instance().send_create_event_signal("DDL", theme, deadline, content, reminder, "Great")
						QMessageBox.information(self, "保存成功",
												f"主题: {theme}\n内容: {content}\n截止时间: {deadline}\n提醒时间: {reminder}")
					else:
						log.info(
							f"修改{_type}事件，事件ID: {self.id},标题：{theme}, 截止时间：{deadline}, 内容：{content}, 提前提醒时间：{reminder}, 重要程度：Great")
						# DDL参数(标题，截止时间，具体内容，提前提醒时间，重要程度)
						Emitter.instance().send_modify_event_signal(self.id, "DDL", theme, deadline, content, reminder,
																	"Great")
						QMessageBox.information(self, f"修改事件{self.id}成功",
												f"主题: {theme}\n内容: {content}\n截止时间: {deadline}\n提醒时间: {reminder}")
						self.id = None

			elif _type == "日程":
				start_date = self.start_date_edit.dateTime().toString("yyyy-MM-dd")  	# 开始日期
				start_time = self.start_time_edit.dateTime().toString("HH:mm")  		# 开始时间
				end_date = self.end_date_edit.dateTime().toString("yyyy-MM-dd")  		# 结束日期
				end_time = self.end_time_edit.dateTime().toString("HH:mm")  			# 结束时间

				if start_date > end_date:
					QMessageBox.warning(self, "警告", "开始日期晚于结束日期")
					return
				if start_date == end_date:
					if start_time > end_time:
						QMessageBox.warning(self, "警告", "开始时间晚于结束时间")
						return

				repeat = self.repeat_combo.currentText()								#是否重复
				repeat_day = None														#星期几重复
				if repeat != "不重复":
					repeat_day = self.chinese_to_english[self.repeat_day_combo.currentText()]
				"""输入：标题，每天开始时间，每天结束时间，开始日期，终止日期，笔记，重要程度，重复类型如("weekly"、"biweekly），重复具体星期"""
				if self.id is None:
					# 新建事件
					log.info(
						f"创建新{_type}事件，标题：{theme}, 开始时间{start_time}, 结束时间{end_time}, 开始日期{start_date}, 结束日期{end_date}, 笔记{content}, 重要程度：'Great',重复类型：{repeat},重复星期：{repeat_day}")
					Emitter.instance().send_create_event_signal("Activity", theme, start_time, end_time, start_date, end_date, content, "Great", repeat, repeat_day)
					QMessageBox.information(self, "保存成功","")
				else:
					log.info(
						f"修改{_type}事件，事件id：{self.id}，标题：{theme}, 开始时间{start_time}, 结束时间{end_time}, 开始日期{start_date}, 结束日期{end_date}, 笔记{content}, 重要程度：'Great',重复类型：{repeat},重复星期：{repeat_day}")
					Emitter.instance().send_modify_event_signal(self.id, "Activity", theme, start_time, end_time, start_date, end_date, content, "Great", repeat, repeat_day)
					QMessageBox.information(self, f"修改事件成功","")
					# 刷新id
					self.id = None
		else:
			QMessageBox.warning(self, "警告", "请填写标题")

	def get_selected_times(self):
		"""返回用户选择的截止时间和提醒时间"""
		deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		reminder = self.reminder_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		return deadline, reminder

	def create_ddl_widgets(self):
		"""创建选项1的所有部件并返回列表"""
		widgets = []

		# 截止时间选择框
		deadline_label = QLabel("截止时间:")
		set_font(deadline_label)
		self.dynamic_layout.addWidget(deadline_label)
		widgets.append(deadline_label)

		# 选择截止时间
		self.deadline_edit = QDateTimeEdit()
		set_font(self.deadline_edit)
		self.deadline_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
		self.deadline_edit.setDateTime(QDateTime.currentDateTime())
		self.deadline_edit.setCalendarPopup(True)  # 在点击时弹出日历
		calendar = self.deadline_edit.calendarWidget()  # 获取日历控件（QCalendarWidget）
		calendar.setStyleSheet("""
										            QCalendarWidget QAbstractItemView:item:hover {  /*鼠标悬停*/
										                background-color: palette(midlight);
										            }
													""")  # 设置日历样式
		self.dynamic_layout.addWidget(self.deadline_edit)
		widgets.append(self.deadline_edit)

		ddl_spacer = QWidget()
		ddl_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
		self.dynamic_layout.addWidget(ddl_spacer)
		widgets.append(ddl_spacer)

		# 提醒时间选择框
		reminder_label = QLabel("提醒时间:")
		set_font(reminder_label)
		self.dynamic_layout.addWidget(reminder_label)
		widgets.append(reminder_label)

		self.reminder_edit = QDateTimeEdit()
		set_font(self.reminder_edit)
		self.reminder_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
		self.reminder_edit.setDateTime(QDateTime.currentDateTime())
		self.reminder_edit.setCalendarPopup(True)
		calendar = self.reminder_edit.calendarWidget()  # 获取日历控件（QCalendarWidget）
		calendar.setStyleSheet("""
							            QCalendarWidget QAbstractItemView:item:hover {  /*鼠标悬停*/
							                background-color: palette(midlight);
							            }
									    """)  # 设置日历样式
		self.dynamic_layout.addWidget(self.reminder_edit)
		widgets.append(self.reminder_edit)

		return widgets

	def create_schedule_widgets(self):
		"""创建选项2的所有部件并返回列表"""
		widgets = []

		# 起止时间
		start_and_end_label = QLabel("起止日期：")
		set_font(start_and_end_label)
		self.dynamic_layout.addWidget(start_and_end_label)
		widgets.append(start_and_end_label)
		# 起始日期
		self.start_date_edit = QDateTimeEdit()
		self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
		self.start_date_edit.setDate(QDate.currentDate())
		self.start_date_edit.setCalendarPopup(True)
		calendar = self.start_date_edit.calendarWidget()  # 获取日历控件（QCalendarWidget）
		calendar.setStyleSheet("""
						            QCalendarWidget QAbstractItemView:item:hover {  /*鼠标悬停*/
						                background-color: palette(midlight);
						            }
								    """)  # 设置日历样式
		set_font(self.start_date_edit)
		self.dynamic_layout.addWidget(self.start_date_edit)
		widgets.append(self.start_date_edit)

		# 起始时间
		self.start_time_edit = QDateTimeEdit()
		self.start_time_edit.setDisplayFormat("HH:mm")
		self.start_time_edit.setTime(QTime.currentTime())
		set_font(self.start_time_edit)
		self.dynamic_layout.addWidget(self.start_time_edit)
		widgets.append(self.start_time_edit)

		# '~'标签
		to_label = QLabel("~")
		set_font(to_label)
		self.dynamic_layout.addWidget(to_label)
		widgets.append(to_label)

		# 结束日期
		self.end_date_edit = QDateTimeEdit()
		self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
		self.end_date_edit.setDate(QDate.currentDate())
		self.end_date_edit.setCalendarPopup(True)
		calendar = self.end_date_edit.calendarWidget()  # 获取日历控件（QCalendarWidget）
		calendar.setStyleSheet("""
								    QCalendarWidget QAbstractItemView:item:hover {  /*鼠标悬停*/
							            background-color: palette(midlight);
						            }
								    """)
		set_font(self.end_date_edit)
		self.dynamic_layout.addWidget(self.end_date_edit)
		widgets.append(self.end_date_edit)

		# 结束时间
		self.end_time_edit = QDateTimeEdit()
		self.end_time_edit.setDisplayFormat("HH:mm")
		self.end_time_edit.setTime(QTime.currentTime())
		set_font(self.end_time_edit)
		self.dynamic_layout.addWidget(self.end_time_edit)
		widgets.append(self.end_time_edit)

		schedule_spacer = QWidget()
		schedule_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
		self.dynamic_layout.addWidget(schedule_spacer)
		widgets.append(schedule_spacer)

		# 重复标签
		repeat_label = QLabel("重复：")
		set_font(repeat_label)
		self.dynamic_layout.addWidget(repeat_label)
		widgets.append(repeat_label)

		# 重复
		self.repeat_combo = QComboBox()
		set_font(self.repeat_combo)
		repeat_days = ("不重复", "每周", "每两周")
		self.repeat_combo.addItems(repeat_days)
		self.dynamic_layout.addWidget(self.repeat_combo)
		widgets.append(self.repeat_combo)
		self.repeat_combo.currentTextChanged.connect(self.update_repeat_dynamic_widgets)

		self.repeat_day_combo = QComboBox()
		set_font(self.repeat_day_combo)
		repeat_days = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")
		self.repeat_day_combo.addItems(repeat_days)
		self.dynamic_layout.addWidget(self.repeat_day_combo)
		widgets.append(self.repeat_day_combo)

		return widgets

	def hide_all_dynamic_widgets(self):
		"""隐藏所有动态部件"""
		for widget in self.ddl_widgets:
			widget.hide()
		for widget in self.schedule_widgets:
			widget.hide()

	def update_dynamic_widgets(self, selected_text):
		"""根据主选项显示/隐藏动态部件"""
		# 首先隐藏所有部件
		self.hide_all_dynamic_widgets()

		if selected_text == "DDL":
			# 显示选项1的部件
			self.group_box.setTitle("添加DDL")
			for widget in self.ddl_widgets:
				widget.show()
		elif selected_text == "日程":
			# 显示选项2的部件
			self.group_box.setTitle("添加日程")
			for widget in self.schedule_widgets:
				widget.show()
			if self.repeat_combo.currentText() == '不重复':
				self.repeat_day_combo.hide()

		else:
			log.error("警告：选择了除DDL和日程以外的种类")

	def update_repeat_dynamic_widgets(self, selected_text):
		"""
		更新关于重复事件选择的选项
		"""
		self.repeat_day_combo.hide()
		if not selected_text == "不重复":
			self.repeat_day_combo.show()
	
	def refresh(self):
		"""
		刷新schedule
		"""
		self.id = None
		self.theme_text_edit.clear()
		self.text_edit.clear()
		self.type_choose_combo.setCurrentText("DDL")
		self.type_choose_combo.setEnabled(True)
