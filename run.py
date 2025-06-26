import sys
import os

# 添加当前目录和 src 目录到模块路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

# 设置资源路径查找函数（用于mac打包）
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(BASE_DIR, relative_path)

# 设置资源路径全局可用（方便插入图片）
os.environ["CHRONOSFLOW_RES"] = resource_path("assets")

# 启动主程序
from src.main import main  # src/main.py 中定义的 main 函数
main()