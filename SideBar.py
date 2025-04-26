from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLineEdit, QFrame, QHBoxLayout
from PySide6.QtGui import QFont, QIcon
from functools import partial
from Emitter import Emitter


class SideBar(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setFrameShape(QFrame.StyledPanel)

		# 信号
		self.emitter = Emitter()

		# 侧边栏内容
		layout = QVBoxLayout()
		layout.setContentsMargins(10, 10, 10, 20)

		# 添加search文本框
		search_layout = QHBoxLayout()
		# 左侧文本框
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
		# 右侧按钮
		btn = QPushButton()
		btn.setIcon(QIcon.fromTheme("system-search"))
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
		btn.setFixedSize(40, 40)
		btn.clicked.connect(self.get_text)
		search_layout.addWidget(btn)

		layout.addLayout(search_layout)

		# 添加按钮
		names = ("Calendar", "Upcoming", "Setting", "Schedule")
		button_font = QFont("微软雅黑", 11)
		for name in names:
			btn = QPushButton(f"{name}")
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
			layout.addWidget(btn)
			#发信号
			btn.clicked.connect(partial(self.emitter.send_page_change_signal, name))

		layout.addStretch()
		self.setLayout(layout)

	# 获取文本框内容TODO:后端
	def get_text(self):
		self.emitter.send_search_signal(self.search_edit.text())
