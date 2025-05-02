from common import *


class SettingsPage(QWidget):
    settings_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 存储路径设置
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("数据存储目录:"))
        
        self.storage_path_edit = QLineEdit()
        self.storage_path_edit.setPlaceholderText("请选择目录")
        path_layout.addWidget(self.storage_path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.select_storage_path)
        path_layout.addWidget(browse_btn)

        # 主题设置
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("应用主题:"))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "系统默认"])
        theme_layout.addWidget(self.theme_combo)
        
        # 通知设置组
        notification_group = QGroupBox("通知设置")
        notification_layout = QVBoxLayout()
        
        # 启用通知复选框
        self.notify_checkbox = QCheckBox("启用通知")
        notification_layout.addWidget(self.notify_checkbox)
        
        # 通知类型
        notify_type_layout = QHBoxLayout()
        notify_type_layout.addWidget(QLabel("通知类型:"))
        
        self.notify_type_combo = QComboBox()
        self.notify_type_combo.addItems(["系统通知", "声音提醒", "两者都使用"])
        notify_type_layout.addWidget(self.notify_type_combo)
        notification_layout.addLayout(notify_type_layout)
        
        notification_group.setLayout(notification_layout)

        # 音量设置组
        volume_group = QGroupBox("音量设置")
        volume_layout = QVBoxLayout()
        
        # 音量滑块
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(10)
        
        # 音量值显示
        self.volume_label = QLabel("音量: 50%")
        self.volume_slider.valueChanged.connect(self.update_volume_label)
        
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        volume_group.setLayout(volume_layout)

        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)

        # 主布局
        layout.addLayout(path_layout)
        layout.addLayout(theme_layout)
        layout.addWidget(notification_group)
        layout.addWidget(volume_group)
        layout.addStretch()
        layout.addWidget(save_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def update_volume_label(self, value):
        """更新音量标签显示"""
        self.volume_label.setText(f"音量: {value}%")

    def select_storage_path(self):
        """使用Tkinter选择目录"""
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(title="选择数据存储目录")
        if path:
            self.storage_path_edit.setText(path)
            #os.makedirs(path, exist_ok=True)
            self.config_path_cpy : str = os.path.join(path, "settings_cpy.json")

    def get_config_path(self):
        """获取配置文件路径"""
        if sys.platform == 'win32':
            # Windows 路径：%USERPROFILE%\AppData\Local\MyApp\settings.json
            config_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'MyApp')
        elif sys.platform == 'darwin':  # macOS
            # macOS/Linux 路径：~/Library/Application Support/MyApp/settings.json
            config_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'MyApp')
        else:  # Linux 或其他 Unix
            # macOS/Linux 路径：~/.config/MyApp/settings.json
            config_dir = os.path.join(os.path.expanduser('~'), '.config', 'MyApp')
        #config_dir = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'MyApp')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'settings.json')

    def get_data_dir(self):
        """获取数据存储目录路径"""
        return os.path.join(self.storage_path_edit.text(), 'AppData')

    def load_settings(self):
        """加载设置"""
        config_path = self.get_config_path()
        print(config_path)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.storage_path_edit.setText(settings.get('storage_path', ''))
                    self.theme_combo.setCurrentText(settings.get('theme', '浅色'))
                    
                    # 加载通知设置
                    self.notify_checkbox.setChecked(settings.get('notifications_enabled', True))
                    self.notify_type_combo.setCurrentText(settings.get('notification_type', '系统通知'))
                
                    # 加载音量设置
                    volume = settings.get('volume', 50)
                    self.volume_slider.setValue(volume)
                    self.update_volume_label(volume)
                    
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载设置失败: {str(e)}")

    def save_settings(self):
        """保存设置并创建完整目录结构"""
        settings = {
            'storage_path': self.storage_path_edit.text(),
            'theme': self.theme_combo.currentText(),
            'notifications_enabled': self.notify_checkbox.isChecked(),
            'notification_type': self.notify_type_combo.currentText(),
            'volume': self.volume_slider.value(),
            'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if not settings['storage_path']:
            QMessageBox.critical(self, "错误", "必须选择有效的存储目录！")
            return

        try:
            # 创建数据目录结构
            data_dir = self.get_data_dir()
            print("data_dir:",data_dir)
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

            # 保存配置文件 (JSON格式)
            config_path = self.get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            with open(self.config_path_cpy, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            # 新增：保存人类可读的设置内容文件
            settings_content_path = os.path.join(data_dir, 'settings_content.txt')
            with open(settings_content_path, 'w', encoding='utf-8') as f:
                f.write(f"""=== 应用程序设置详情 ===
            
    存储路径: {settings['storage_path']}
    当前主题: {settings['theme']}
    通知设置: {'启用' if settings['notifications_enabled'] else '禁用'}
    通知类型: {settings['notification_type']}
    音量级别: {settings['volume']}%
    最后修改: {settings['last_modified']}

    === 原始JSON数据 ===
    {json.dumps(settings, indent=4, ensure_ascii=False)}
    """)

            QMessageBox.information(
                self, 
                "保存成功", 
                f"""设置已保存！
            
        配置文件位置: {config_path}
        数据目录: {data_dir}
        设置详情已保存至: {settings_content_path}"""
            )
            self.settings_saved.emit()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")