from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLineEdit, QFrame,QHBoxLayout
from PySide6.QtGui import QFont


class SideBar(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setFrameShape(QFrame.StyledPanel)
		self.setStyleSheet("""
            background-color: white;
            border-right: 1px solid #ccc;
        """)

		# 侧边栏内容
		layout = QVBoxLayout()
		layout.setContentsMargins(10, 10, 10, 20)

		# 添加search文本框
		search_layout = QHBoxLayout()
		#左侧文本框
		self.search_edit = QLineEdit()
		self.search_edit.setPlaceholderText("请输入名称或日期...")
		self.search_edit.setStyleSheet("""
						            QLineEdit {
						                padding: 8px;
						                border: 1px solid #ccc;
						                border-radius: 4px;
						                font-size: 14px;
						            }
						            QLineEdit:focus {
						                border: 1px solid #4CAF50;
						            }
						        """)
		search_layout.addWidget(self.search_edit)
		#右侧按钮
		btn=QPushButton("Q")
		btn.setFixedSize(42,42)
		btn.clicked.connect(self.get_text)
		search_layout.addWidget(btn)

		layout.addLayout(search_layout)

		# 添加按钮
		name = ("Calendar", "Upcoming", "Setting")
		button = {}
		button_font = QFont("微软雅黑", 11)
		for i in name:
			btn = QPushButton(f"{i}")
			btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
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
			btn.setFont(button_font)
			button[i] = btn
			layout.addWidget(btn)

			btn.clicked.connect(lambda checked, name=i: self.button_click(name))  # 点击

		layout.addStretch()
		self.setLayout(layout)

	def button_click(self, name):
		print(name)

	# 获取文本框内容
	def get_text(self):
		text = self.search_edit.text()
		print(f"{text}")
