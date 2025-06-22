from common import *
from functools import partial
from Emitter import Emitter
from FontSetting import set_font


class SideBar(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setFrameShape(QFrame.StyledPanel)

		self.setStyleSheet(
			"""QFrame{
                           background-color:#D1D9E0
                           }"""
		)

		# ===侧边栏内容===
		layout = QVBoxLayout()
		layout.setContentsMargins(10, 10, 10, 20)
		name_label = QLabel("ChronosFlow")
		name_label.setAlignment(Qt.AlignCenter)
		font = QFont("Helvetica Neue", 24, QFont.Bold)  # 更具未来感的字体
		name_label.setFont(font)
		name_label.setStyleSheet("""
		    color: #1E90FF; /* 蓝色字体 */
		    font-size: 24px;
		    letter-spacing: 2px; /* 增加字母间距 */
		    font-family: 'Helvetica Neue', sans-serif;
		""")
		layout.addWidget(name_label)
		# 把sidebar撑开
		spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
		layout.addItem(spacer)

		# ===添加功能按钮===
		names = ("Calendar", "Upcoming", "Weekview", "Setting")
		buttons = [
			("日历", QStyle.SP_FileDialogListView),
			("日程", QStyle.SP_FileDialogDetailedView),
			("周视图", QStyle.SP_FileDialogContentsView),
			("设置", QStyle.SP_DriveCDIcon)
		]

		for i in range(len(names)):
			btn = QPushButton(f"{buttons[i][0]}")
			btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: black;
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
			set_font(btn, 1)

			# 图标
			icon = self.style().standardIcon(buttons[i][1])
			btn.setIcon(icon)
			btn.setIconSize(QSize(20, 20))

			layout.addWidget(btn)
			# 连接按钮与切换页面信号
			btn.clicked.connect(partial(Emitter.instance().send_page_change_signal, names[i]))
		layout.addStretch()
		self.setLayout(layout)
