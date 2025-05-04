from common import *
from Emitter import Emitter

log = logging.getLogger(__name__)


class Schedule(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.standard_date = None
		self.date = ['0000', '00', '00']  # 日期
		self.datetime = ['00', '00']  # TODO:调整具体时间（小时，分钟）
		layout = QVBoxLayout(self)

		self.date_label = QLabel()
		layout.addWidget(self.date_label, alignment=Qt.AlignmentFlag.AlignCenter)

		# 单行文本框
		self.theme_text_edit = QLineEdit()
		self.theme_text_edit.setFont(QFont("Arial", 12))
		self.theme_text_edit.setPlaceholderText("主题")
		self.theme_text_edit.setFixedHeight(50)
		layout.addWidget(self.theme_text_edit)

		# 创建多行文本框
		self.text_edit = QPlainTextEdit()
		self.text_edit.setFont(QFont("Arial", 12))
		self.text_edit.setPlaceholderText("内容")
		layout.addWidget(self.text_edit)
  
		# 截止时间选择框
		self.deadline_label = QLabel("截止时间:")
		layout.addWidget(self.deadline_label)

		self.deadline_edit = QDateTimeEdit()
		self.deadline_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
		self.deadline_edit.setDateTime(QDateTime.currentDateTime())
		self.deadline_edit.setCalendarPopup(True)
		layout.addWidget(self.deadline_edit)

		# 提醒时间选择框
		self.reminder_label = QLabel("提醒时间:")
		layout.addWidget(self.reminder_label)

		self.reminder_edit = QDateTimeEdit()
		self.reminder_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
		self.reminder_edit.setDateTime(QDateTime.currentDateTime())
		self.reminder_edit.setCalendarPopup(True)
		layout.addWidget(self.reminder_edit)

		# 创建按钮
		button_layout = QHBoxLayout()
		layout.addLayout(button_layout)

		btn_name = ("Save", "Open")
		for i in range(len(btn_name)):
			btn = QPushButton(btn_name[i])
			if i == 0:
				btn.clicked.connect(self.create_new_event)
			elif i == 1:
				btn.clicked.connect(self.load_created_event)

			btn.setStyleSheet("""
								QPushButton {
					                background-color: transparent;
					                border: 1px solid #d0d0d0;
					                border-radius: 4px;
					                padding: 25px;
					                qproperty-alignment: 'AlignCenter';
					            }
					            QPushButton:hover {
					                background-color: #d0d0d0;
					                border-radius: 4px;
					            }
					            QPushButton:pressed {
									background-color: #e0e0e0;
								}
							""")

			button_layout.addWidget(btn)

		# 状态栏
		self.status_label = QLabel()
		layout.addWidget(self.status_label)

	def receive_date(self, date: QDate):
		'''
		接收date，并进行格式转化
		'''
		# 为了方便后面数据进行储存，这里转换过程中间储存了QDate格式，但在GUI界面的显示方式仍为年月日
		self.standard_date = date
		self.date = self.standard_date.toString("yyyy-MM-dd").split('-')
		log.info(f"收到日期信息{self.date[0]}年{self.date[1]}月{self.date[2]}日")
		self.date_label.setText(f"{self.date[0]}年{self.date[1]}月{self.date[2]}日")

	def create_new_event(self):
		'''
		保存内容，暂时后端只做了DDL类 TODO:支持不同形式event的储存
		传送内容为event类别（DDL），该类别所需参数
		TODO:向Notice的schedule_notice发信号
		'''
		theme = self.theme_text_edit.text()
		content = self.text_edit.toPlainText()
		deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		reminder = self.reminder_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		notify_time = self.reminder_edit.dateTime()
		"""
		time = QTime(int(self.datetime[0]), int(self.datetime[1]))
		datetime = QDateTime(self.standard_date, time)
		datetime_str = datetime.toString("yyyy-MM-dd HH:mm")
		test_advance_time = datetime.addDays(-1)
		test_advance_time_str = test_advance_time.toString("yyyy-MM-dd HH:mm")
  		"""
		log.info(
			f"创建新事件，标题：{theme}, 截止时间：{deadline}, 内容：{content}, 提前提醒时间：{reminder}, 重要程度：Great"),
		# DDL参数(标题，截止时间，具体内容，提前提醒时间，重要程度)
		Emitter.instance().send_create_event_signal("DDL", theme, deadline,
													content, reminder, "Great")
		Emitter.instance().send_signal_to_schedule_notice(theme, content, notify_time)
		if theme and content and deadline and reminder:
			# 这里可以添加保存事件的逻辑
			QMessageBox.information(self, "成功", f"主题: {theme}\n内容: {content}\n截止时间: {deadline}\n提醒时间: {reminder}")
			# TODO 保存到后端数据库
		else:
			QMessageBox.warning(self, "警告", "请填写所有信息")

	# 加载内容TODO:后端
	def load_created_event(self):
		# TODO:从后端接收内容;弹出搜索框？
		pass
	def get_selected_times(self):
		"""返回用户选择的截止时间和提醒时间"""
		deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		reminder = self.reminder_edit.dateTime().toString("yyyy-MM-dd HH:mm")
		return deadline, reminder
