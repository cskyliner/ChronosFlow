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
        #delete_button = DeleteButton(parent=graphics_view.viewport())
        self.view = view

        palette = QApplication.palette()
        self.background_color = palette.color(QPalette.Base)
        self.text_color = palette.color(QPalette.Text)
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
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRect(self.rect())

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
        #if self.connection_line:
         #   self.scene().removeItem(self.connection_line)
          #  self.connection_line = None

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
        #log.info(f"self.current_week = {self.current_week}")
        self.update_week(QDate.currentDate())
        
    def init_ui(self):
     
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
       
        # 创建一个包含时间轴和内容视图的主场景
        self.main_scene = QGraphicsScene()
        # 创建主视图
        #self.main_view = QGraphicsView(self.main_scene)
        #self.main_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.main_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_view = QGraphicsView(self.main_scene)
        self.main_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_view.setDragMode(QGraphicsView.ScrollHandDrag)  # 支持拖拽滚动
        #self.delete_button = DeleteButton(parent=self.main_view.viewport())
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
            
            # 绘制小时分隔线（贯穿时间轴）
            
        # 设置时间轴视图的位置和大小
        #self.time_axis_view.setSceneRect(0, 0, 60, self.time_slot_count * self.hour_height)

    def update_week(self, week_date: QDate):
        """更新显示指定周"""
        #self.main_scene.clear()
        self.setup_time_axis()  # 重新绘制时间轴
        
        # 计算周日期范围
        self.monday = week_date.addDays(1 - week_date.dayOfWeek())
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

        # 设置内容视图的位置和大小
        #self.content_view.setSceneRect(0, 0, total_width, total_height)
        
        # 更新滚动条范围
        #self.horizontal_scrollbar.setRange(0, max(0, total_width - self.main_view.width() + 60))
        #self.horizontal_scrollbar.setPageStep(self.main_view.width() - 60)
        
        #self.vertical_scrollbar.setRange(0, max(0, total_height - self.main_view.height()))
        #self.vertical_scrollbar.setPageStep(self.main_view.height())
        
        # 更新视图位置
        #self.update_views_position()
        
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
            # 假设有一个矩形区域 (x, y, width, height)


    def setup_day_columns(self):
        """创建日期列"""
        start_y = 30  # 表头高度
        
        for i in range(7):
            col_rect = QRectF(60 + i*self.day_width, start_y, self.day_width, self.time_slot_count * self.hour_height)
            col = WeekDayColumn(col_rect, self.dates[i])
            self.main_scene.addItem(col)
            
            # 添加时间格子
            for h in range(self.time_slot_count):
                #cell_rect = QRectF(0, h*self.hour_height, self.day_width, self.hour_height)
                #cell = QGraphicsRectItem(cell_rect, col)
                #cell = ScheduleAreaItem(cell_rect, col)
                #cell.setAcceptHoverEvents(True)
                #cell.setPen(QPen(Qt.NoPen))
                #self.main_scene.addItem(cell)
                cell_x = 60 + i * self.day_width
                cell_y = start_y + h * self.hour_height
                cell_rect = QRectF(0, 0, self.day_width, self.hour_height)
                cell = ScheduleAreaItem(QTime(h,0), QTime(h+1, 0), self.monday.addDays(i) ,cell_rect)
                #cell.double_clicked.connect(lambda e,cell = cell: self.schedule_area_clicked.emit(e))
                cell.double_clicked.connect(partial(self.schedule_area_clicked.emit))
                cell.setPos(cell_x, cell_y)
                self.main_scene.addItem(cell)      
                self.cell_map[(i + 1, self.start_hour + h)] = cell         
                # 绑定点击事件
                #cell.mousePressEvent = lambda event, d=self.dates[i], h=h+self.start_hour: \
                 #   self.handle_time_click(d, h, event)
                    
            line_pen = QPen(self.text_color)  # 统一的灰色分割线颜色
            line_pen.setWidth(1)  # 统一的线宽，防止出现不同粗细
            line = self.main_scene.addLine(
                60 + i * self.day_width, start_y,  # 从每一列的左边缘开始
                60 + i * self.day_width, start_y + self.time_slot_count * self.hour_height,  # 到每列的底边缘
                line_pen  # 使用统一的笔刷设置
            )        
        # 添加贯穿所有列的小时分隔线（与时间轴对齐）
        for h in range(self.time_slot_count + 1):
            y = start_y + h * self.hour_height
            line = self.main_scene.addLine(0, y, 60 + self.day_width * 7, y, QPen(QColor("#3cf907")))

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
        #self.clear_schedule_blocks()
        self.events = []
        first_date = self.dates[0].toString("yyyy-MM-dd")
        end_date = self.dates[-1].toString("yyyy-MM-dd")
        self.events = EventSQLManager.get_events_between_twodays(first_date,end_date)
        if(len(self.events) == 0):
            log.info(f"Weekview load_schedules: 没有找到任何活动日程")
        else:
            log.info(f"Weekview load_schedules: 找到 {len(self.events)} 条活动日程\n"
                     +"\n".join(f"- {event.title} @ {event.start_date}-{event.end_date}" for event in self.events))
            
        for event in self.events:
            self.add_schedule_item(event)

    def add_schedule_item(self, event:ActivityEvent):
        """添加日程块到视图"""
        start_t = QTime.fromString(event.start_time, "HH:mm")
        end_t = QTime.fromString(event.end_time, "HH:mm")
        
        try:
            repeat_days = json.loads(event.repeat_days)
            if isinstance(repeat_days, str):
                repeat_days = [repeat_days]            
        except Exception as e:
            log.error(f"解析 repeat_days 失败: {event.repeat_days} - {e}")
            return        
        if not repeat_days:
            #repeat_days = []
            log.warning(f"{event.title} 没有 repeat_days")
            #return
        #log.info(f"{event.title} repeat_days: {repeat_days} type: {type(repeat_days)}")
        #for day_str in repeat_days:
         #   weekday = self.mp.get(day_str)
          #  if weekday is None:
           #     log.error(f"未知的星期缩写: {day_str}")
            #    continue
        dt = QDateTime.fromString(event.datetime, "yyyy-MM-dd HH:mm")
        date = dt.date()
        weekday = date.dayOfWeek()
        start_hour = start_t.hour()
        key = (weekday, start_hour)        
        # 只显示当前周的日程
        #if start_dt.date() not in self.dates:
        #   return
        cell:ScheduleAreaItem = self.cell_map.get(key)
        if not cell:
            log.error(f"添加的日程:{event.title} (weekday, start_hour) = {key} 找不到对应的时间格子")
            return  # 不在当前视图范围       
        # 计算局部坐标下的 y 和高度
        else:
            log.info(f"添加的日程:{event.title} (weekday, start_hour) = {key} 对应的时间格子位置x:{cell.x()}, y:{cell.y()}\
                width:{cell.rect().width()} height:{cell.rect().height()}")
        start_min = start_t.minute()
        y = (start_min / 60) * self.hour_height
        duration_min = max(start_t.secsTo(end_t) // 60, 40)
        height = (duration_min / 60) * self.hour_height

        rect = QRectF(0, 0, self.day_width - 4, height)
        block = ScheduleBlockItem(rect, event, self.main_view)
        block.double_clicked.connect(lambda e: self.schedule_double_clicked.emit(e))
        #block = ScheduleBlockItem(rect, event)
        block.setZValue(1)  # 保证高于所有 cell（它们默认 Z=0）
        block.setPos(cell.pos() + QPointF(2, y))  # 手动设置位置
        self.main_scene.addItem(block)
        self.schedule_block_items.append(block)
        #block.setParentItem(cell)
        block.del_btn_clicked.connect(lambda e: self.schedule_del_btn_clicked.emit(e))       
        
        # 计算位置
        #col_index = start_dt.date().dayOfWeek() - 1
        #x = 60 + col_index * self.day_width  # 从时间轴右侧开始
        
        # 计算垂直位置
        #start_hour = start_dt.time().hour()
        #start_min = start_dt.time().minute()
        #y = 30 + (start_hour - self.start_hour) * self.hour_height + (start_min / 60) * self.hour_height
        
        # 计算高度
        #duration_min = start_dt.secsTo(end_dt) // 60
        #if duration_min <= 0:
        #    duration_min = 30  # 最小持续时间
        #height = (duration_min / 60) * self.hour_height
        
        #rect = QRectF(x + 2, y, self.day_width - 4, height)
        #block = ScheduleBlockItem(rect, event)
        #block.clicked.connect(lambda e: self.schedule_clicked.emit(e))
        #self.main_scene.addItem(block)
    def clear_schedule_blocks(self):
        log.info("clear_schedule_blocks被调用")
        if(self.schedule_block_items is None):
            log.info("clear_schedule_blocks: self.schedule_block_items 为空")
            return
        log.info(f"clear_schedule_blocks: 当前schedule_block_items数量为: {len(self.schedule_block_items)}")
        for block in self.schedule_block_items:
            if block.scene():  # 确保 block 仍存在于场景中
                self.main_scene.removeItem(block)
        self.schedule_block_items.clear()        
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
        #view_height = self.height()
        time_column_width = 60
        #header_height = 30
        current_rect = self.main_scene.sceneRect()  # 获取当前场景的矩形
        self.day_width = (view_width - time_column_width) / 7
        #self.hour_height = (view_height - header_height) / (self.end_hour - self.start_hour)
        #self.time_slot_count = self.end_hour - self.start_hour
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
