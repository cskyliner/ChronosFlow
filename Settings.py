from common import *
from Emitter import Emitter
from ioporter.course_importer import CourseScheduleImporter
import json
from FontSetting import set_font

log = logging.getLogger(__name__)


class SettingsPage(QWidget):
	"""设置页面"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("设置")
		self.setup_ui()
		self.load_settings()

	def setup_ui(self):
		layout = QVBoxLayout()

		# 存储路径设置
		path_group = QGroupBox("存储目录")
		set_font(path_group)
		path_group.setStyleSheet("""
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
		path_layout = QHBoxLayout()
		path_label = QLabel("数据存储目录:")
		set_font(path_label)
		path_layout.addWidget(path_label)

		self.storage_path_edit = QLineEdit()
		self.storage_path_edit.setFixedHeight(35)
		self.storage_path_edit.setStyleSheet("""QLineEdit {
			border-radius: 5px;
			border:1px solid palette(mid);
			background:transparent
		}""")
		self.storage_path_edit.setPlaceholderText("请选择目录")
		set_font(self.storage_path_edit)
		path_layout.addWidget(self.storage_path_edit)

		browse_btn = QPushButton("浏览...")
		browse_btn.setFixedSize(80, 35)
		browse_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                    padding: 0px;
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
		set_font(browse_btn)
		browse_btn.clicked.connect(self.select_storage_path)
		path_layout.addWidget(browse_btn)

		path_group.setLayout(path_layout)

		# 主题设置
		theme_group = QGroupBox("主题")
		set_font(theme_group)
		theme_group.setStyleSheet("""
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

		theme_layout = QHBoxLayout()
		theme_label = QLabel("应用主题:")
		set_font(theme_label)
		theme_layout.addWidget(theme_label)

		self.theme_combo = QComboBox()
		self.theme_combo.addItems(["浅色", "深色", "系统默认"])
		set_font(self.theme_combo)
		theme_layout.addWidget(self.theme_combo)

		theme_group.setLayout(theme_layout)

		# 通知设置组
		notification_group = QGroupBox("通知设置")
		notification_group.setStyleSheet("""
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
		set_font(notification_group)
		notification_layout = QHBoxLayout()

		# 启用通知复选框
		self.notify_checkbox = QCheckBox("启用通知")
		set_font(self.notify_checkbox)
		notification_layout.addWidget(self.notify_checkbox)

		spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
		notification_layout.addItem(spacer)

		# 通知类型
		notify_type_label = QLabel("通知类型:")
		set_font(notify_type_label)
		notification_layout.addWidget(notify_type_label)

		self.notify_type_combo = QComboBox()
		self.notify_type_combo.addItems(["系统通知", "声音提醒", "两者都使用"])
		set_font(self.notify_type_combo)
		notification_layout.addWidget(self.notify_type_combo)

		notification_group.setLayout(notification_layout)

		# 音量设置组
		volume_group = QGroupBox("音量设置")
		volume_group.setStyleSheet("""
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
		set_font(volume_group)
		volume_layout = QVBoxLayout()

		# 音量滑块
		self.volume_slider = QSlider(Qt.Horizontal)
		self.volume_slider.setRange(0, 100)
		self.volume_slider.setTickPosition(QSlider.TicksBelow)
		self.volume_slider.setTickInterval(10)

		# 音量值显示
		self.volume_label = QLabel("音量: 50%")
		set_font(self.volume_label)
		self.volume_slider.valueChanged.connect(self.update_volume_label)

		volume_layout.addWidget(self.volume_slider)
		volume_layout.addWidget(self.volume_label)
		volume_group.setLayout(volume_layout)

		# 壁纸路径
		wallpaper_group = QGroupBox("壁纸")
		wallpaper_group.setStyleSheet("""
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
		set_font(wallpaper_group)
		wallpaper_layout = QHBoxLayout()
		wallpaper_label = QLabel("壁纸路径:")
		set_font(wallpaper_label)
		wallpaper_layout.addWidget(wallpaper_label)

		self.wallpaper_path_edit = QLineEdit()
		self.wallpaper_path_edit.setFixedHeight(35)
		self.wallpaper_path_edit.setStyleSheet("""QLineEdit {
					border-radius: 5px;
					border:1px solid palette(mid);
					background:transparent
				}""")
		self.wallpaper_path_edit.setPlaceholderText("请选择壁纸路径")
		set_font(self.wallpaper_path_edit)
		wallpaper_layout.addWidget(self.wallpaper_path_edit)

		wallpaper_btn = QPushButton("浏览...")
		wallpaper_btn.setFixedSize(80, 35)
		wallpaper_btn.setStyleSheet("""
		                QPushButton {
		                    background-color: transparent;
		                    border: 1px solid palette(mid);
		                    border-radius: 4px;
		                    padding: 0px;
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
		set_font(wallpaper_btn)
		wallpaper_btn.clicked.connect(self.select_wallpaper_path)
		wallpaper_layout.addWidget(wallpaper_btn)

		wallpaper_group.setLayout(wallpaper_layout)

		# 课表路径
		excel_group = QGroupBox("课表")
		excel_group.setStyleSheet("""
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
		set_font(excel_group)

		ttl_excel_layout = QVBoxLayout()

		excel_date_layout = QHBoxLayout()
		ttl_excel_layout.addLayout(excel_date_layout)
		start_time_label = QLabel("这个学期开始第一天（周一）的日期：")
		set_font(start_time_label)
		excel_date_layout.addWidget(start_time_label)
		self.start_date_edit = QDateTimeEdit()
		self.start_date_edit.setCalendarPopup(True)
		calendar = self.start_date_edit.calendarWidget()  # 获取日历控件（QCalendarWidget）
		calendar.setStyleSheet("""
								            QCalendarWidget QAbstractItemView:item:hover {  /*鼠标悬停*/
								                background-color: palette(midlight);
								            }
										    """)  # 设置日历样式
		self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
		excel_date_layout.addWidget(self.start_date_edit)
		self.start_date_edit.setDate(QDate.currentDate())

		excel_layout = QHBoxLayout()
		ttl_excel_layout.addLayout(excel_layout)
		excel_label = QLabel("课表路径:")
		set_font(excel_label)
		excel_layout.addWidget(excel_label)

		self.excel_path_edit = QLineEdit()
		self.excel_path_edit.setFixedHeight(35)
		self.excel_path_edit.setStyleSheet("""QLineEdit {
							border-radius: 5px;
							border:1px solid palette(mid);
							background:transparent
						}""")
		self.excel_path_edit.setPlaceholderText("请选择课表路径")
		set_font(self.excel_path_edit)
		excel_layout.addWidget(self.excel_path_edit)

		excel_btn = QPushButton("浏览...")
		excel_btn.setFixedSize(80, 35)
		excel_btn.setStyleSheet("""
				                QPushButton {
				                    background-color: transparent;
				                    border: 1px solid palette(mid);
				                    border-radius: 4px;
				                    padding: 0px;
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
		set_font(excel_btn)
		excel_btn.clicked.connect(self.select_excel_path)
		excel_layout.addWidget(excel_btn)

		excel_group.setLayout(ttl_excel_layout)

		# 保存按钮
		save_btn = QPushButton("保存设置")
		save_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                    padding: 0px;
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
		save_btn.setFixedSize(100, 40)
		set_font(save_btn)
		save_btn.clicked.connect(lambda: self.save_settings(reminder=True))  # 添加reminder参数使得手动保存与默认保存区分开来

		# 主布局
		layout.addWidget(path_group)
		layout.addWidget(theme_group)
		theme_group.hide()
		layout.addWidget(notification_group)
		notification_group.hide()
		layout.addWidget(volume_group)
		volume_group.hide()
		layout.addWidget(wallpaper_group)
		layout.addWidget(excel_group)
		layout.addStretch()
		layout.addWidget(save_btn, alignment=Qt.AlignRight)
		self.setLayout(layout)

	def update_volume_label(self, value):
		"""更新音量标签显示"""
		self.volume_label.setText(f"音量: {value}%")

	def get_default_storage_path(self) -> str:
		"""获取默认存储路径（即用户主目录）"""
		if sys.platform == 'win32':
			# Windows 路径：%USERPROFILE%\AppData\Local\MyApp\settings.json
			config_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'MyApp')
		elif sys.platform == 'darwin':  # macOS
			# macOS/Linux 路径：~/Library/Application Support/MyApp/settings.json
			config_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'MyApp')
		else:  # Linux 或其他 Unix
			# macOS/Linux 路径：~/.config/MyApp/settings.json
			config_dir = os.path.join(os.path.expanduser('~'), '.config', 'MyApp')
		return config_dir

	def select_storage_path(self):
		"""选择储存路径"""
		if sys.platform == 'darwin':
			# macOS 直接使用Qt自带文件对话框选择目录
			path = QFileDialog.getExistingDirectory(self, "选择数据存储目录")
		else:
			root = tk.Tk()
			root.withdraw()
			path = filedialog.askdirectory(title="选择数据存储目录")
		if path:
			log.info(f"用户选择的存储路径: {path}")
			self.storage_path_edit.setText(path)

	# os.makedirs(path, exist_ok=True)
	# self.config_path_cpy : str = os.path.join(path, "settings_cpy.json")

	def select_wallpaper_path(self):
		"""选择壁纸文件"""
		if sys.platform == 'darwin':
			file_filter = "Images (*.jpg *.png)"
			file_path, _ = QFileDialog.getOpenFileName(self, "选择壁纸文件", "", file_filter)
		else:
			root = tk.Tk()
			root.withdraw()
			file_path = filedialog.askopenfilename(
				title="选择壁纸文件",
				filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
			)
		if file_path:
			log.info(f"用户选择的壁纸文件: {file_path}")
			self.wallpaper_path_edit.setText(file_path)

	def select_excel_path(self):
		"""选择 Excel 文件"""
		if sys.platform == 'darwin':  # macOS
			file_filter = "Excel Files (*.xlsx *.xls *.csv)"
			file_path, _ = QFileDialog.getOpenFileName(
				self,
				"选择 Excel 文件",  # 对话框标题
				"",  # 默认打开路径（空表示当前目录）
				file_filter
			)
		else:  # Windows/Linux
			root = tk.Tk()
			root.withdraw()
			file_path = filedialog.askopenfilename(
				title="选择 Excel 文件",
				filetypes=[
					("Excel 文件", "*.xlsx *.xls"),  # .xlsx 和 .xls
					("CSV 文件", "*.csv"),  # .csv
					("所有文件", "*.*")  # 允许选择所有文件（可选）
				]
			)
		if file_path:
			log.info(f"用户选择的 Excel 文件: {file_path}")
			self.excel_path_edit.setText(file_path)

	def get_config_path(self) -> str:
		"""获取配置文件路径"""
		# 获取默认存储路径
		config_dir = self.get_default_storage_path()
		# config_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'MyApp')
		os.makedirs(config_dir, exist_ok=True)
		return os.path.join(config_dir, 'settings.json')

	def get_data_dir(self) -> str:
		"""获取数据存储目录路径"""
		return os.path.join(self.storage_path_edit.text(), 'AppData')

	def load_settings(self):
		"""加载设置"""
		config_path = self.get_config_path()
		log.info(f"配置文件路径: {config_path}")
		if os.path.exists(config_path):
			try:
				with open(config_path, 'r', encoding='utf-8') as f:
					settings = json.load(f)
					self.storage_path_edit.setText(settings.get('storage_path', ''))
					self.theme_combo.setCurrentText(settings.get('theme', '系统默认'))

					# 加载通知设置
					self.notify_checkbox.setChecked(settings.get('notifications_enabled', True))
					self.notify_type_combo.setCurrentText(settings.get('notification_type', '系统通知'))

					# 加载音量设置
					volume = settings.get('volume', 50)
					self.volume_slider.setValue(volume)
					self.update_volume_label(volume)

					# 加载壁纸路径
					self.wallpaper_path = settings.get('wallpaper_path', '')
					self.wallpaper_path_edit.setText(self.wallpaper_path)

					#课表
					self.start_date_edit.setDate(QDate.fromString(settings.get('course_start_date'), "yyyy-MM-dd"))
					self.excel_path=settings.get('excel_path','')
					self.excel_path_edit.setText(self.excel_path)
					log.info(f"加载设置: {settings}")
					# 发送信号通知储存路径
					Emitter.instance().send_storage_path(
						os.path.join(settings.get('storage_path', ''), "AppData", "Database"))
					CourseScheduleImporter.init_importer("/Users/kylin/Desktop/timetable大一下.xls","2025-02-17",16)
					# CourseScheduleImporter.extract_info()

			except Exception as e:
				QMessageBox.warning(self, "错误", f"加载设置失败: {str(e)}")
		else:
			# 如果配置文件不存在，创建新文件并写入默认设置，默认储存路径为用户主目录
			default_settings = {
				"storage_path": self.get_default_storage_path(),
				"theme": "系统默认",
				"notifications_enabled": True,
				"notification_type": "系统通知",
				"volume": 50,
				"wallpaper_path": "无壁纸",
				"excel_path": "无课表",
				'course_start_date': "无"
			}
			try:
				with open(config_path, 'w', encoding='utf-8') as f:
					json.dump(default_settings, f, ensure_ascii=False, indent=4)
				# 加载默认设置
				self.storage_path_edit.setText(default_settings['storage_path'])
				self.theme_combo.setCurrentText(default_settings['theme'])
				self.notify_checkbox.setChecked(default_settings['notifications_enabled'])
				self.notify_type_combo.setCurrentText(default_settings['notification_type'])
				volume = default_settings['volume']
				self.volume_slider.setValue(volume)
				self.update_volume_label(volume)
				self.wallpaper_path_edit.setText(default_settings["wallpaper_path"])
				self.excel_path_edit.setText(default_settings["excel_path"])
				self.start_date_edit.setDate(QDate.currentDate())

				self.save_settings(reminder=False)
				log.info(f"创建默认设置: {default_settings}")
				# 发送信号通知默认储存路径
				Emitter.instance().send_storage_path(
					os.path.join(default_settings['storage_path'], "AppData", "Database"))
			except Exception as e:
				QMessageBox.warning(self, "错误", f"创建并写入默认设置失败: {str(e)}")

	def save_settings(self, reminder: bool = True):
		"""保存设置并创建完整目录结构"""
		settings = {
			'storage_path': self.storage_path_edit.text(),
			'theme': self.theme_combo.currentText(),
			'notifications_enabled': self.notify_checkbox.isChecked(),
			'notification_type': self.notify_type_combo.currentText(),
			'volume': self.volume_slider.value(),
			'wallpaper_path': self.wallpaper_path_edit.text(),
			'excel_path': self.excel_path_edit.text(),
			'course_start_date': self.start_date_edit.date().toString("yyyy-MM-dd"),
			'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		}

		if not settings['storage_path']:
			QMessageBox.critical(self, "错误", "必须选择有效的存储目录！")
			return

		try:
			# 创建数据目录结构
			data_dir = self.get_data_dir()
			log.info(f"data_dir:{data_dir}")
			subdirs = ['Database', 'Attachments', 'Backups', 'Exports']

			for subdir in subdirs:
				os.makedirs(os.path.join(data_dir, subdir), exist_ok=True)

			# 创建说明文件
			readme_path = os.path.join(data_dir, 'README.txt')
			with open(readme_path, 'w', encoding='utf-8') as f:
				f.write(f"""此目录由应用程序自动生成
    创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    目录结构说明:
    - Database: 主数据库文件
    - Attachments: 附件存储
    - Backups: 自动备份
    - Exports: 导出数据
    - settings_content.txt: 当前配置详情
    """)

			# 保存配置文件及其在data_dir中的副本 (JSON格式)
			config_path = self.get_config_path()
			with open(config_path, 'w', encoding='utf-8') as f:
				json.dump(settings, f, indent=4, ensure_ascii=False)
			with open(os.path.join(data_dir, "settings_cpy.json"), 'w', encoding='utf-8') as f:
				json.dump(settings, f, indent=4, ensure_ascii=False)
			# 保存人类可读的设置内容文件
			settings_content_path = os.path.join(data_dir, 'settings_content.txt')
			with open(settings_content_path, 'w', encoding='utf-8') as f:
				f.write(f"""=== 应用程序设置详情 ===
            
    存储路径: {settings['storage_path']}
    当前主题: {settings['theme']}
    通知设置: {'启用' if settings['notifications_enabled'] else '禁用'}
    通知类型: {settings['notification_type']}
    音量级别: {settings['volume']}%
    壁纸路径: {settings['wallpaper_path']}%
    最后修改: {settings['last_modified']}

    === 原始JSON数据 ===
    {json.dumps(settings, indent=4, ensure_ascii=False)}
    """)
			# 提示用户保存成功
			print(f"[Debug] reminder 参数值为: {reminder}")
			if reminder is True:
				QMessageBox.information(
					self,
					"保存成功",
					f"""设置已保存！
            
        配置文件位置: {config_path}
        数据目录: {data_dir}
        设置详情已保存至: {settings_content_path}"""
				)
			log.info("设置已保存")
			# 发送信号通知储存路径
			Emitter.instance().send_storage_path(os.path.join(settings['storage_path'], "AppData", "Database"))

		except Exception as e:
			QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")
