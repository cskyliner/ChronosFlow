from PySide6.QtWidgets import QPlainTextEdit, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QFileDialog, \
	QLineEdit
from PySide6.QtGui import QFont
from Emitter import TempEmitter


class Schedule(QWidget):
	def __init__(self, height=None, width=None, parent=None):
		super().__init__(parent)

		self.height = height
		self.width = width
		self.date = None
		self.date_label = QLabel()

		layout = QVBoxLayout(self)

		layout.addWidget(self.date_label)

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

		# 创建按钮
		button_layout = QHBoxLayout()
		layout.addLayout(button_layout)

		btn_name = ("Save", "Open")
		for i in range(len(btn_name)):
			btn = QPushButton(btn_name[i])
			if i == 0:
				btn.clicked.connect(self.save_text)
			elif i == 1:
				btn.clicked.connect(self.load_text)

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

	# 接收date
	def receive_signal(self, date):
		self.date_label.setText(date.toString("yyyy年MM月dd日"))
		self.date = date

	# 保存内容 TODO:发送日期
	def save_text(self):
		filename, _ = QFileDialog.getSaveFileName(self, "保存文件")
		if filename:
			emitter = TempEmitter()
			emitter.send_signal(filename, self.theme_text_edit.text(), self.text_edit.toPlainText())  # 路径,主题,内容

	# 加载内容
	def load_text(self):
		filename, _ = QFileDialog.getOpenFileName(self, "打开文件")
		if filename:
			emitter = TempEmitter()
			emitter.send_signal(filename)
# TODO:从后端接收内容
