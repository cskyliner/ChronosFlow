from common import *
from functools import partial
from Emitter import Emitter
from SetFont import common_set_font


class SideBar(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setFrameShape(QFrame.StyledPanel)

		# ===侧边栏内容===
		layout = QVBoxLayout()
		layout.setContentsMargins(10, 10, 10, 20)

		title_font = QFont()
		title_font.setFamilies(["Inter", "Helvetica Neue", "Segoe UI", "Arial"])
		title_font.setPointSize(20)
		name_label=QLabel("ChronosFlow\n————————")
		name_label.setAlignment(Qt.AlignCenter)
		name_label.setFont(title_font)
		layout.addWidget(name_label)

		#把sidebar撑开
		spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
		layout.addItem(spacer)

		# ===添加功能按钮===
		names = ("Calendar", "Upcoming", "Setting")
		for name in names:
			btn = QPushButton(f"{name}")
			btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 25px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: palette(midlight); /*轻微高亮*/
                    border-radius: 4px;
                }
                QPushButton:pressed {
					background-color: palette(mid);
				}
            """)
			common_set_font(btn,1)
			layout.addWidget(btn)
			# 连接按钮与切换页面信号
			btn.clicked.connect(partial(Emitter.instance().send_page_change_signal, name))
		layout.addStretch()
		self.setLayout(layout)