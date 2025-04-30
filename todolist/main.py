from common import *
from MainWindow import MainWindow
from SignalConnect import connect_event_signal
def init_platform_style(a):
	#根据系统选择UI风格
	if sys.platform == "win32":
		a.setStyle(QStyleFactory.create("windows"))
	elif sys.platform == "darwin":
		a.setStyle(QStyleFactory.create("macintosh"))
	elif sys.platform.startswith("linux"):
		a.setStyle(QStyleFactory.create("fusion"))

# ===配置输出日志，方便查询报错信息与位置===
logging.basicConfig(
    level=logging.INFO,  # 设置最低日志级别
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
    handlers=[
        logging.StreamHandler(sys.stdout),   # 输出到控制台
    ]
)

if __name__ == "__main__":
	app = QApplication([])
	init_platform_style(app)
	app.setWindowIcon(QIcon("pic/todolist.png"))
	connect_event_signal()  # 连接前后端信号
	main_window = MainWindow(1000, 600, 140, 100)
	main_window.show()
	app.exec()
