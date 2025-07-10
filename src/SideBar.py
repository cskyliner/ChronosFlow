from src.common import *
from functools import partial
from src.Emitter import Emitter
from src.FontSetting import set_font
from src.Settings import SettingsDialog


class SideBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            """
                SideBar {
                background-color: palette(midlight);
            }

            """
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
        names = ("Calendar", "Upcoming", "Weekview", "HeatMap","AIChat")
        buttons = [
            ("日历", QStyle.SP_FileDialogListView),
            ("日程", QStyle.SP_FileDialogDetailedView),
            ("周视图", QStyle.SP_FileDialogContentsView),
            ("热力图", QStyle.SP_FileDialogDetailedView),
            ("AI助手", QStyle.SP_FileDialogDetailedView)
        ]

        for i in range(len(names)):
            btn = QPushButton(f"{buttons[i][0]}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: palette(text);
                    border: none;
                    padding: 25px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: palette(light); /*轻微高亮*/
                    border-radius: 4px;
                }
                QPushButton:pressed {
                    background-color: palette(mid);
                }
            """)
            set_font(btn, 1)
            # 图标
            if i == 0:
                img_path = os.path.join(os.environ["CHRONOSFLOW_RES"], "calendar.svg")
                pixmap = QPixmap(img_path)
                btn.setIcon(QIcon(pixmap))
            elif i == 1:
                img_path = os.path.join(os.environ["CHRONOSFLOW_RES"], "upcoming.svg")
                pixmap = QPixmap(img_path)
                btn.setIcon(QIcon(pixmap))		
            elif i == 2:
                img_path = os.path.join(os.environ["CHRONOSFLOW_RES"], "weekview.svg")
                pixmap = QPixmap(img_path)
                btn.setIcon(QIcon(pixmap))
            elif i == 3:
                img_path = os.path.join(os.environ["CHRONOSFLOW_RES"], "heat-map.svg")
                pixmap = QPixmap(img_path)
                btn.setIcon(QIcon(pixmap))
            elif i == 4:
                img_path = os.path.join(os.environ["CHRONOSFLOW_RES"], "aichat.svg")
                pixmap = QPixmap(img_path)
                btn.setIcon(QIcon(pixmap))
            else:
                icon = self.style().standardIcon(buttons[i][1])
                btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))

            layout.addWidget(btn)
            # 连接按钮与切换页面信号
            btn.clicked.connect(partial(Emitter.instance().send_page_change_signal, names[i]))
        layout.addStretch()
        setting_button = QPushButton()
        setting_button.setFixedSize(35, 35)
        icon_path = os.path.join(os.environ["CHRONOSFLOW_RES"], "settings.svg")
        pixmap = QPixmap(icon_path)
        setting_button.setIcon(QIcon(pixmap))
        setting_button.setIconSize(QSize(20, 20))
        setting_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: palette(light);
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: palette(mid);
            }
        """)
        layout.addWidget(setting_button, alignment=Qt.AlignHCenter)
        setting_button.clicked.connect(self.open_setting)
        self.setLayout(layout)

    def open_setting(self):
        dialog = SettingsDialog(self)
        dialog.exec()
