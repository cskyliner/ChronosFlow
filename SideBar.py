from common import * 
from functools import partial
from Emitter import Emitter


class SideBar(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setFrameShape(QFrame.StyledPanel)

		# ===侧边栏内容===
		layout = QVBoxLayout()
		layout.setContentsMargins(10, 10, 10, 20)

		# ===添加search文本框===
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
		# ===右侧按钮===
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

		# ===添加功能按钮===
		names = ("Calendar", "Upcoming", "Setting", "Schedule")
		#使用Qt的字体回退机制，解决在Mac上找不到字体报错的问题 FIXME:前端可能需要调试一下字体大小，以及缩放问题
		button_font = QFont()
		button_font.setFamilies(["Segoe UI", "Helvetica", "Arial"])
		button_font.setPointSize(15)
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
			#连接按钮与切换页面信号
			btn.clicked.connect(partial(Emitter.instance().send_page_change_signal, name))
		layout.addStretch()
		self.setLayout(layout)

	# 获取文本框内容 TODO:后端
	def get_text(self):
		Emitter.instance().send_search_signal(self.search_edit.text())
