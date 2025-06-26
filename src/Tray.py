from common import *

if sys.platform == 'darwin':
	import pystray
	import rumps
	import threading
from PIL import Image

log = logging.getLogger(__name__)


# ---------------------- 系统托盘类 ----------------------
class Tray(QObject):
	show_main = Signal()
	show_floating = Signal()
	exit_app = Signal()
	notification_received = Signal(object)
	activated_response = Signal()

	def __init__(self, app, parent=None, icon_path=None):
		super().__init__(parent)
		self.app = app or QApplication.instance()
		self.icon_path = icon_path
		self.notification_widgets = []
		self.frame_index = 0  # 当前为动图第几帧
		self.frames = []  # 存储动图
		self._init_tray()
		self._connect_signals()

	def _init_tray(self):
		"""安全初始化托盘"""
		try:
			if platform.system() == 'Windows':
				self._init_windows_tray()
			else:
				self._init_macos_tray()
		except Exception as e:
			log.error(f"托盘初始化失败: {str(e)}")
			self._create_fallback_tray()

	def _init_windows_tray(self):
		"""Windows托盘实现"""
		log.info("初始化托盘")
		self.tray = QSystemTrayIcon(self)  # 关键修复：设置parent
		self._setup_icon()
		self._create_menu()
		self.tray.activated.connect(self._on_tray_activated)
		self.tray.show()

	def _init_macos_tray(self):
		"""macOS 托盘"""
		self.tray = QSystemTrayIcon(self)

		# 加载 .icns 图标
		icns_path = os.path.abspath("pic/icon.iconset/icon_512x512@2x.png")
		icon = QIcon(icns_path)
		self.tray.setIcon(icon)

		menu = QMenu()
		menu.addAction(QAction("打开主窗口", menu, triggered=lambda: self.show_main.emit()))
		menu.addAction(QAction("打开悬浮窗", menu, triggered=lambda: self.show_floating.emit()))
		menu.addAction(QAction("退出", menu, triggered=lambda: self.exit_app.emit()))
		self.tray.setContextMenu(menu)
		self.tray.activated.connect(self._on_tray_activated)
		self.tray.show()
		
	def _create_fallback_tray(self):
		"""创建备用托盘"""
		self.tray = QSystemTrayIcon(self)
		pixmap = QPixmap(64, 64)
		pixmap.fill(Qt.GlobalColor.blue)
		self.tray.setIcon(QIcon(pixmap))
		self.tray.show()

	def _setup_icon(self):
		"""确保始终有有效图标"""
		if self.icon_path and os.path.exists(self.icon_path):
			self.tray.setIcon(QIcon(self.icon_path))
		elif self.app and not self.app.windowIcon().isNull():
			self.tray.setIcon(self.app.windowIcon())
		else:
			pixmap = QPixmap(64, 64)
			pixmap.fill(Qt.GlobalColor.darkGreen)
			self.tray.setIcon(QIcon(pixmap))

	def _create_menu(self):
		"""安全创建菜单"""
		menu = QMenu()

		actions = [
			("打开主窗口", lambda: self.show_main.emit()),
			("打开悬浮窗", lambda: self.show_floating.emit()),
			("退出", lambda: self.exit_app.emit())
		]

		for text, callback in actions:
			action = QAction(text, menu)
			action.triggered.connect(callback)
			menu.addAction(action)

		self.tray.setContextMenu(menu)

	def _create_pystray_menu(self):
		"""创建pystray菜单（macOS）"""
		return pystray.Menu(
			pystray.MenuItem('打开主窗口', self._pystray_show_main),
			pystray.MenuItem('打开悬浮窗', self._pystray_show_floating),
			pystray.MenuItem('退出', self._pystray_exit)
		)

	# macOS
	def _create_pillow_icon(self):
		"""生成默认托盘图标"""
		icon_path = "pic/icon.iconset/icon_32x32@2x.png"
		icon_image = Image.open(icon_path)
		return icon_image

	def load_frames(self, frame_folder='pic', frame_count=36):
		"""TODO:macos托盘加载多帧PNG图像"""
		self.frames = []
		path = f"{frame_folder}/icon_bar.png"
		img = Image.open(path).convert("RGBA")
		self.frames.append(img)
		# for i in range(frame_count):
		# 	path = f"{frame_folder}/frame_{i:02d}.png"
		# 	img = Image.open(path).convert("RGBA")
		# 	self.frames.append(img)
		
	@Slot(object)
	def show_notification(self, data: tuple):
		"""显示通知"""
		event = data[0]
		if platform.system() == 'Windows':
			self.tray.showMessage(event.title, event.notes, QSystemTrayIcon.Information, 2000)
		else:
			rumps.notification(event.title, event.notes, "")

	# macOS菜单回调函数
	def _pystray_show_main(self, icon, item):
		self.show_main.emit()

	def _pystray_show_floating(self, icon, item):
		self.show_floating.emit()

	def _pystray_exit(self, icon, item):
		self.exit_app.emit()

	def shutdown(self):
		"""清理资源"""
		if platform.system() == 'Windows':
			self.tray.hide()
		else:
			# rumps 不需要显式停止，App 退出时自动清理
			pass

	def _connect_signals(self):
		"""连接信号与槽"""
		self.notification_received.connect(self.show_notification)

	def _on_tray_activated(self, reason):
		if reason == QSystemTrayIcon.Trigger:
			self.activated_response.emit()
