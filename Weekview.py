from common import *
from Upcoming import FloatingButton, DeleteButton
from functools import partial
from events.Event import *
from events.EventManager import EventSQLManager
log = logging.getLogger(__name__)
class TimeAxisItem(QGraphicsRectItem):
    """左侧时间轴项"""
    def __init__(self, rect, time_str):
        super().__init__(rect)
        self.time_str = time_str

        palette = QApplication.palette()
        self.background_color = palette.color(QPalette.Base)
        self.text_color = palette.color(QPalette.Text)
        
    def paint(self, painter, option, widget=None):
        painter.setFont(QFont("Arial", 8))
        painter.setPen(self.text_color)
        painter.drawText(self.rect().adjusted(2, 0, 0, 0), Qt.AlignLeft | Qt.AlignVCenter, self.time_str)

class ScheduleBlockItem(QGraphicsRectItem,QObject):
    """日程块图形项"""
    clicked = Signal(BaseEvent)
    del_btn_clicked = Signal(BaseEvent)
    double_clicked = Signal(BaseEvent)
    hover_signal = Signal(BaseEvent)

    def __init__(self, rect: QRectF, event, view:QGraphicsView, parent=None):
        QObject.__init__(self)  # 初始化 QObject
        QGraphicsRectItem.__init__(self, rect)  # 初始化 QGraphicsRectItem
        self.event:ActivityEvent = event
        self.view = view

        self._bg_color = QColor("#DBE6D9")  # 苔藓灰绿
        self._border_color = QColor("#C5D1C3")  # 边框色
        self._border_width = 1.0

        palette = QApplication.palette()
        self.background_color = palette.color(QPalette.Base)
        self.text_color = QColor("#000000")
        self.light_color = palette.color(QPalette.Highlight)

        self.delete_button:DeleteButton = DeleteButton(parent=self.view.viewport())
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.setStyleSheet("""
			QPushButton {
				background-color: rgba(255, 80, 80, 0.1);  /* 半透明红色背景 */
				border: 1px solid rgba(255, 80, 80, 0.3);
				border-radius: 6px;
				min-width: 28px;
				min-height: 28px;
				padding: 0;
				padding-top: -2px;  /* 关键对齐参数 */
				color: #FF5050;
				font-size: 14px;
				font-weight: 300;
				text-align: center;
			}
			QPushButton:hover {
				background-color: rgba(255, 80, 80, 0.15);
				border: 1px solid rgba(255, 80, 80, 0.5);
				color: #E03C3C;
				font-size: 16px;
			}
			QPushButton:pressed {
				background-color: rgba(224, 60, 60, 0.2);
				border: 1px solid rgba(224, 60, 60, 0.7);
				color: #C03030;
				padding-top: 1px;
			}
		""")
        
        self.delete_button.bind_event(self.event)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.hide()
        self.setAcceptHoverEvents(True)
        self.setBrush(QBrush(self.background_color))
        self.setPen(self.text_color)

    def on_delete_clicked(self):
        log.info(f" weekview:on_delete_clicked 尝试删除事件：{self.event.title}")
        self.delete_button.hide()
        self.del_btn_clicked.emit(self.event)  # 发出删除信号        

    def paint(self, painter, option, widget=None):
        # 画背景
        # 绘制背景
        painter.setBrush(QBrush(self._bg_color))
        # 设置边框
        pen = QPen(self._border_color, self._border_width)
        if self.isSelected():
            pen.setStyle(Qt.DashLine)  # 选中时显示虚线边框
        painter.setPen(pen)
        # 绘制圆角矩形
        rect = self.rect().adjusted(1, 1, -1, -1)  # 向内缩进1像素
        painter.drawRoundedRect(rect, 5, 5)  # 5px圆角

        # 设置字体
        painter.setPen(self.text_color)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        # 显示 event 信息
        title = self.event.title
        start = self.event.start_time[-5:]  # 提取 HH:mm
        end = self.event.end_time[-5:]
        time_range = f"{start} - {end}"

        # 文字显示（最多两行）
        text_rect = self.rect().adjusted(4, 2, -4, -2)  # 留边距
        self.text = f"{title}({self.event.repeat_type})\n{time_range}"
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignVCenter)
        text_option.setWrapMode(QTextOption.WordWrap)
        painter.drawText(text_rect, self.text, text_option)

    def mousePressEvent(self, event):
        self.clicked.emit(self.event)
        
    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit(self.event)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(self.light_color))

        # 显示按钮在右下角
        scene = self.scene()
        view = scene.views()[0]
        block_br = self.sceneBoundingRect().bottomRight()
        margin = 6
        button_scene_pos = QPointF(
            block_br.x() - self.delete_button.width() - margin,
            block_br.y() - self.delete_button.height() - margin
        )
        button_view_pos = view.mapFromScene(button_scene_pos)
        self.delete_button.move(button_view_pos)
        self.delete_button.show()
        self.delete_button.raise_()

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(self.background_color))  # 鼠标离开时恢复
        self.delete_button.hide()

class WeekDayColumn(QGraphicsRectItem):
    """单日列容器"""
    def __init__(self, rect, date):
        super().__init__(rect)
        self.date = date

        palette = QApplication.palette()
        self.background_color = palette.color(QPalette.Base)
        self.text_color = palette.color(QPalette.Text)

        self.setPen(self.text_color)
        self.setBrush(self.background_color)

class WeekView(QWidget):
    """周视图主组件"""
    schedule_area_clicked = Signal(object)
    schedule_del_btn_clicked = Signal(BaseEvent)
    schedule_clicked = Signal(BaseEvent)
    schedule_double_clicked = Signal(BaseEvent)
    time_clicked = Signal(QDateTime)  # 点击时间格子信号
    add_schedule = Signal(QDateTime)
    floating_button:FloatingButton = None
    def __init__(self):
        super().__init__()
        self.start_hour = 0  # 开始时间
        self.end_hour = 24   # 结束时间
        self.hour_height = 60  # 每个小时的高度
        self.time_slot_count = self.end_hour - self.start_hour
        self.day_width = 100  
        self.cell_map = {}  # {(weekday: int, hour: int): ScheduleAreaItem} 用于定位时间格子 # Monday=1, Sunday=7
        self.mp = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7}
        self.schedule_block_items = list()
        self.events = None

        palette = QApplication.palette()
        self.background_color = palette.color(QPalette.Base)
        self.text_color = palette.color(QPalette.Text)

        self.init_ui()
        self.setup_time_axis()
        self.current_week = QDate.currentDate().weekNumber()[0]
        self.current_week_date = QDate.currentDate()
        self.update_week(self.current_week_date.addDays(1 - self.current_week_date.dayOfWeek()))

    def init_ui(self):
    
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        # 添加顶部导航栏
        self.nav_bar = QHBoxLayout()
        self.nav_bar.setContentsMargins(10, 5, 10, 5)
        self.nav_bar.setSpacing(20)
        
        # 上周按钮
        self.prev_week_btn = QLabel("<")
        self.prev_week_btn.setAlignment(Qt.AlignCenter)
        self.prev_week_btn.setMinimumSize(30, 30)
        self.prev_week_btn.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border-radius: 15px;
                color: #333;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: #e0e0e0;
                color: #0078d7;
            }
        """)
        self.prev_week_btn.mousePressEvent = self.on_prev_week_click
        
        # 周显示标签
        self.week_display = QLabel()
        self.week_display.setAlignment(Qt.AlignCenter)
        self.week_display.setMinimumHeight(30)
        self.week_display.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        
        # 下周按钮
        self.next_week_btn = QLabel(">")
        self.next_week_btn.setAlignment(Qt.AlignCenter)
        self.next_week_btn.setMinimumSize(30, 30)
        self.next_week_btn.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border-radius: 15px;
                color: #333;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: #e0e0e0;
                color: #0078d7;
            }
        """)
        self.next_week_btn.mousePressEvent = self.on_next_week_click
        
        self.nav_bar.addWidget(self.prev_week_btn)
        self.nav_bar.addWidget(self.week_display)
        self.nav_bar.addWidget(self.next_week_btn)
        self.main_layout.addLayout(self.nav_bar)
        # 创建一个包含时间轴和内容视图的主场景
        self.main_scene = QGraphicsScene()
        # 创建主视图
        self.main_view = QGraphicsView(self.main_scene)
        self.main_view.setStyleSheet("""
        /* 垂直滚动条 */
        QScrollBar:vertical {
            border: none;
            background: palette(base);
            width: 3px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #1E90FF;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: #1E90FF;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        /* 水平滚动条 */
        QScrollBar:horizontal {
            border: none;
            background: palette(base);
            height: 3px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal {
            background: #1E90FF;
            min-width: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #1E90FF;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 0px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
        """)
        self.main_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_view.setDragMode(QGraphicsView.ScrollHandDrag)  # 支持拖拽滚动
        self.main_layout.addWidget(self.main_view)    
        # 添加水平滚动条
        #self.horizontal_scrollbar = QScrollBar(Qt.Horizontal)
        #self.horizontal_scrollbar.valueChanged.connect(self.horizontal_scroll)
        
        # 添加垂直滚动条
        #self.vertical_scrollbar = QScrollBar(Qt.Vertical)
        #self.vertical_scrollbar.valueChanged.connect(self.vertical_scroll)
        
        # 布局
        #scroll_layout = QHBoxLayout()
        #scroll_layout.addWidget(self.main_view)
        #scroll_layout.addWidget(self.vertical_scrollbar)
        
        #self.main_layout.addLayout(scroll_layout)
        #self.main_layout.addWidget(self.horizontal_scrollbar)
        
        # 时间轴视图（作为主场景的一部分）
        #self.time_axis_view = QGraphicsView(self.main_scene)
        #self.time_axis_view.setFixedWidth(60)
        #self.time_axis_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.time_axis_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 主内容视图（作为主场景的一部分）
        #self.content_view = QGraphicsView(self.main_scene)
        #self.content_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.content_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 鼠标滚轮事件
        #self.time_axis_view.wheelEvent = self.main_wheel_event
        #self.content_view.wheelEvent = self.main_wheel_event
    # 上周按钮点击事件
    def on_prev_week_click(self, event):
        if event.button() == Qt.LeftButton:
            # 计算上周日期
            prev_week_date = self.monday.addDays(-7)
            self.update_week(prev_week_date)
            #self.update_week_display(prev_week_date)
    
    # 下周按钮点击事件
    def on_next_week_click(self, event):
        if event.button() == Qt.LeftButton:
            # 计算下周日期
            next_week_date = self.monday.addDays(7)
            self.update_week(next_week_date)
            #self.update_week_display(next_week_date)
    
    # 更新周显示标签
    def update_week_display(self, week_date:QDate):
        start_date = week_date.toString("MM月dd日")
        end_date = week_date.addDays(6).toString("MM月dd日")
        self.week_num = week_date.weekNumber()[0]
        self.year = week_date.year()
        self.week_display.setText(f"{self.year}年 第{self.week_num}周 ({start_date}-{end_date})")
        
    def main_wheel_event(self, event):
        """处理主视图的鼠标滚轮事件"""
        scroll_speed = 80
        delta = event.angleDelta().y()
        
        # 按住Ctrl键时水平滚动，否则垂直滚动
        if event.modifiers() & Qt.ControlModifier:
            self.horizontal_scrollbar.setValue(
                self.horizontal_scrollbar.value() - delta // scroll_speed
            )
        else:
            self.vertical_scrollbar.setValue(
                self.vertical_scrollbar.value() - delta // scroll_speed
            )
            
    def horizontal_scroll(self, value):
        """水平滚动处理"""
        self.content_view.horizontalScrollBar().setValue(value)
        self.update_views_position()
        self.content_view.update()  # 确保视图更新

    def vertical_scroll(self, value):
        """垂直滚动处理"""
        self.time_axis_view.verticalScrollBar().setValue(value)
        self.content_view.verticalScrollBar().setValue(value)
        self.update_views_position()
        self.content_view.update()  # 确保视图更新
        
    def update_views_position(self):
        """更新视图位置"""
        # 同步时间轴和内容视图的垂直位置
        self.time_axis_view.verticalScrollBar().setValue(
            self.content_view.verticalScrollBar().value()
        )
        
        # 同步内容视图的水平位置
        h_value = self.content_view.horizontalScrollBar().value()
        
        # 调整视图的位置
        self.time_axis_view.setGeometry(0, 0, 60, self.main_view.height())
        self.content_view.setGeometry(60 - h_value, 0,  # 调整水平位置
                                    self.main_view.width() - 60, 
                                    self.main_view.height())
        
    def setup_time_axis(self):
        """初始化时间轴"""
        # 创建时间轴背景
        bg_rect = QRectF(0, 0, 60, 30 + self.time_slot_count * self.hour_height)
        bg_item = QGraphicsRectItem(bg_rect)
        bg_item.setBrush(QBrush(self.background_color))
        bg_item.setPen(self.text_color)
        self.main_scene.addItem(bg_item)
        
        # 绘制时间轴和小时分隔线
        for i in range(self.time_slot_count + 1):  # +1 绘制最后一条线
            y = i * self.hour_height
            
            # 绘制时间标签（只在整点绘制）
            if i < self.time_slot_count:
                time = QTime(self.start_hour + i, 0)
                time_str = f"{time.hour():02d}:00"
                rect = QRectF(0, y, 60, self.hour_height)
                item = TimeAxisItem(rect, time_str)
                self.main_scene.addItem(item)

    def update_week(self, monday_date: QDate):
        """更新显示指定周"""
        self.clear_schedule_blocks()
        self.update_week_display(monday_date)
        self.setup_time_axis()  # 重新绘制时间轴
        
        # 计算周日期范围
        self.monday = monday_date
        self.dates = [self.monday.addDays(i) for i in range(7)]
        
        # 创建日期列头
        self.setup_day_headers()
        
        # 创建日期列
        self.setup_day_columns()
        
        # 添加已有日程
        self.load_schedules()
        
        # 设置主场景的大小
        total_width = 60 + self.day_width * 7  # 时间轴宽度 + 7天宽度
        total_height = 30 + self.time_slot_count * self.hour_height  # 30是表头高度
        self.main_scene.setSceneRect(0, 0, total_width, total_height)

    def setup_day_headers(self):
        """创建日期表头"""
        header_height = 30
        
        for i, date in enumerate(self.dates):
            rect = QRectF(60 + i*self.day_width, 0, self.day_width, header_height)
            header = QGraphicsRectItem(rect)
            header.setBrush(QBrush(self.background_color))
            self.main_scene.addItem(header)
            
            # 添加日期文本
            text = f"{date.month()}月{date.day()}日  {['周一','周二','周三','周四','周五','周六','周日'][i]}"
            text_item = QGraphicsSimpleTextItem(text, header)
            text_item.setFont(QFont("Microsoft YaHei", 9))
            text_item.setBrush(QBrush(self.text_color))
            text_item.setPos(rect.x() + 12, rect.y() + 5)

    def setup_day_columns(self):
        """创建日期列"""
        start_y = 30  # 表头高度
        
        for i in range(7):
            col_rect = QRectF(60 + i*self.day_width, start_y, self.day_width, self.time_slot_count * self.hour_height)
            col = WeekDayColumn(col_rect, self.dates[i])
            self.main_scene.addItem(col)
            
            # 添加时间格子
            for h in range(self.time_slot_count):
                cell_x = 60 + i * self.day_width
                cell_y = start_y + h * self.hour_height
                cell_rect = QRectF(0, 0, self.day_width, self.hour_height)
                cell = ScheduleAreaItem(QTime(h,0), QTime(h+1, 0), self.monday.addDays(i) ,cell_rect)
                cell.double_clicked.connect(partial(self.schedule_area_clicked.emit))
                cell.setPos(cell_x, cell_y)
                self.main_scene.addItem(cell)      
                self.cell_map[(i + 1, self.start_hour + h)] = cell         
                    
            line_pen = QPen(self.text_color)  # 统一的灰色分割线颜色
            line_pen.setWidth(1)  # 统一的线宽，防止出现不同粗细
            self.main_scene.addLine(
                60 + i * self.day_width, start_y,  # 从每一列的左边缘开始
                60 + i * self.day_width, start_y + self.time_slot_count * self.hour_height,  # 到每列的底边缘
                line_pen  # 使用统一的笔刷设置
            )        
        # 添加贯穿所有列的小时分隔线（与时间轴对齐）
        for h in range(self.time_slot_count + 1):
            y = start_y + h * self.hour_height
            self.main_scene.addLine(30, y, 60 + self.day_width * 7, y, QPen(QColor(180, 180, 180, 80)))

    def handle_time_click(self, date, hour, event):
        """处理时间格子点击"""
        time = QTime(hour, 0)
        # 使用QDate和QTime创建QDateTime
        dt = QDateTime(date, time)
        dt.setTime(QTime(hour, 0))
        self.time_clicked.emit(dt)
        
        # 右键菜单
        if event.button() == Qt.RightButton:
            menu = QMenu()
            menu.addAction("添加日程", lambda: self.add_schedule.emit(dt))
            menu.exec(event.screenPos())

    def load_schedules(self):
        """加载周的日程"""
        self.clear_schedule_blocks()
        self.events = []
        first_date = self.dates[0].toString("yyyy-MM-dd")
        end_date = self.dates[-1].toString("yyyy-MM-dd")
        self.events = EventSQLManager.get_events_between_twodays(first_date,end_date)
        if(len(self.events) == 0):
            log.info(f"Weekview load_schedules week{self.week_num}({first_date}~{end_date}): 没有找到任何活动日程")
        else:
            log.info(f"Weekview load_schedules week{self.week_num}({first_date}~{end_date}): 找到 {len(self.events)} 条活动日程\n"
                    +"\n".join(f"- {event.title} @ {event.start_date}-{event.end_date}" for event in self.events))
            
        for event in self.events:
            self.add_schedule_item(event)

    def add_schedule_item(self, event:ActivityEvent):
        """添加日程块到视图"""
        start_t = QTime.fromString(event.start_time, "HH:mm")
        end_t = QTime.fromString(event.end_time, "HH:mm")

        dt = QDateTime.fromString(event.datetime, "yyyy-MM-dd HH:mm")
        date = dt.date()
        weekday = date.dayOfWeek()
        start_hour = start_t.hour()
        key = (weekday, start_hour)        

        cell:ScheduleAreaItem = self.cell_map.get(key)
        # 判断是否在当前视图范围
        if not cell:
            log.error(f"添加的日程:{event.title} (weekday, start_hour) = {key} 找不到对应的时间格子")
            return
        # 计算局部坐标下的 y 和高度
        start_min = start_t.minute()
        y = (start_min / 60) * self.hour_height
        duration_min = max(start_t.secsTo(end_t) // 60, 40)
        height = (duration_min / 60) * self.hour_height

        rect = QRectF(0, 0, self.day_width - 4, height)
        block = ScheduleBlockItem(rect, event, self.main_view)
        block.double_clicked.connect(lambda e: self.schedule_double_clicked.emit(e))

        block.setZValue(1)  # 保证高于所有 cell（它们默认 Z=0）
        block.setPos(cell.pos() + QPointF(2, y))  # 手动设置位置
        self.main_scene.addItem(block)
        self.schedule_block_items.append(block)
        block.del_btn_clicked.connect(lambda e: self.schedule_del_btn_clicked.emit(e))       
        
    def clear_schedule_blocks(self):
        log.info("clear_schedule_blocks被调用")
        if not self.schedule_block_items:
            log.info("clear_schedule_blocks: 没有需要移除的日程块")
            return
        
        log.info(f"clear_schedule_blocks: 正在移除 {len(self.schedule_block_items)} 个日程块")
        try:
            for block in self.schedule_block_items:
                if block.scene():
                    self.main_scene.removeItem(block)
        except Exception as e:
            log.error(f"clear_schedule_blocks: 移除日程块时出错: {e}")
        self.schedule_block_items.clear()
        log.info("clear_schedule_blocks: 日程块移除完成")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.recalculate_dimensions()
        #self.main_view.fitInView(self.main_scene.sceneRect(), Qt.IgnoreAspectRatio)
        self.main_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        log.info(f"Scene rect:{self.main_scene.sceneRect()}")
        self.update_view_geometry()

    def recalculate_dimensions(self):
        """根据当前窗口大小重新计算 day_width 和 hour_height"""
        view_width = self.width()
        time_column_width = 60
        current_rect = self.main_scene.sceneRect()  # 获取当前场景的矩形
        self.day_width = (view_width - time_column_width) / 7
        self.main_scene.setSceneRect(0, 0, view_width, current_rect.height())

    def update_view_geometry(self):
        """根据新的大小更新格子和其他组件的位置"""
        self.main_scene.clear()  # 清空场景，重新绘制
        self.setup_time_axis()  # 重新绘制时间轴
        self.setup_day_headers()  # 重新绘制日期头
        self.setup_day_columns()  # 重新绘制日期列
        self.load_schedules()  # 重新加载日程


class ScheduleAreaItem(QObject,QGraphicsRectItem):
    double_clicked:Signal = Signal(object)
    def __init__(self, begin_time:QTime, end_time: QTime, date:QDate, rect, parent=None):
        #super().__init__(rect, parent)
        QObject.__init__(self, parent)
        QGraphicsRectItem.__init__(self, rect, parent)
        self.begin_time = begin_time
        self.end_time = end_time
        self.date = date
        palette = QApplication.palette()
        self.background_color = palette.color(QPalette.Base)
        self.text_color = palette.color(QPalette.Text)

        self.setBrush(QBrush(self.background_color))
        self.setPen(self.text_color)
        self.setAcceptHoverEvents(True)
        
    def hoverEnterEvent(self, event):
        self.setBrush(QColor("#2ba4c6"))  # 鼠标悬停时变为金色

    def hoverLeaveEvent(self, event):
        self.setBrush(self.background_color)  # 鼠标离开时恢复

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit((self.begin_time, self.end_time,self.date))
