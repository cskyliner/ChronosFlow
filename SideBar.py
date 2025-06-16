from common import *
from functools import partial
from Emitter import Emitter
from FontSetting import set_font


class SideBar(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setFrameShape(QFrame.StyledPanel)

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
		display_names = ("日历", "日程", "周视图", "设置")

		# 根据系统类型选择图标
		system_icons = self.get_system_appropriate_icons()

		for i in range(len(names)):
			btn = QPushButton(display_names[i])
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
			set_font(btn, 1)

			# 图标
			icon_type = system_icons[i]
			icon = self.style().standardIcon(icon_type)
			btn.setIcon(icon)
			btn.setIconSize(QSize(20, 20))

			layout.addWidget(btn)
			# 连接按钮与切换页面信号
			btn.clicked.connect(partial(Emitter.instance().send_page_change_signal, names[i]))
		layout.addStretch()
		self.setLayout(layout)


def get_system_appropriate_icons(self):
	"""返回当前系统最适合的图标枚举列表"""
	system_type = sys.platform

	# Windows系统图标
	if system_type == "windows":
		return (
			QStyle.SP_FileDialogListView,  # 日历
			QStyle.SP_FileDialogDetailedView,  # 日程
			QStyle.SP_FileDialogContentsView,  # 周视图
			QStyle.SP_DriveCDIcon  # 设置（使用光盘图标代替齿轮）
		)
	# macOS系统图标
	elif system_type == "macos":
		return (
			QStyle.SP_FileDialogListView,  # 日历
			QStyle.SP_FileDialogDetailedView,  # 日程
			QStyle.SP_FileDialogContentsView,  # 周视图
			QStyle.SP_TitleBarMenuButton  # 设置（使用菜单图标）
		)
	# Linux及其他系统图标
	else:
		return (
			QStyle.SP_FileDialogListView,  # 日历
			QStyle.SP_FileDialogDetailedView,  # 日程
			QStyle.SP_FileDialogContentsView,  # 周视图
			QStyle.SP_ComputerIcon  # 设置（使用计算机图标）
		)
