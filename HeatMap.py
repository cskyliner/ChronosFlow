from common import *
from calendar import monthrange
import dataclasses
from events.Event import *
from events.EventManager import EventSQLManager
LIGHT_THEME_COLORS = [
    "#eeeeee", "#c6e48b", "#7bc96f", "#239a3b", "#196127"
]

DARK_THEME_COLORS = [
    "#222222", "#4e7933", "#6dc36d", "#a0e883", "#e5ffb2"
]
class DayItem(QGraphicsRectItem):
    def __init__(self, date: QDate, count: int, rect: QRectF):
        super().__init__(rect)
        self.date = date
        self.count = count 
        self.setBrush(QBrush(self.map_color(count)))
        self.setAcceptHoverEvents(True)
        self.setToolTip(f"{date.toString()}:\n{count} events")
        self.setPen(QPen(Qt.NoPen))

    def hoverEnterEvent(self, event):
        # 在鼠标屏幕坐标处显示系统 tooltip
        pos = event.screenPos()
        QToolTip.showText(pos, f"{self.date.toString()}:\n{self.count} events")
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        # 鼠标移出时隐藏 tooltip
        QToolTip.hideText()
        super().hoverLeaveEvent(event)

    def map_color(self, count: int):
        # 颜色映射，todo
        # 判断是否深色模式
        is_dark = QApplication.palette().color(QPalette.Window).value() < 128
        color_map = DARK_THEME_COLORS if is_dark else LIGHT_THEME_COLORS

        if count == 0:
            return QColor(color_map[0])
        elif count <= 3:
            return QColor(color_map[1])
        elif count <= 6:
            return QColor(color_map[2])
        elif count <= 10:
            return QColor(color_map[3])
        else:
            return QColor(color_map[4])
        

class MonthBlock(QGraphicsItemGroup):
    def __init__(self,year:int,month:int,data_list:dict,cell_size=12, spacing=2):
        super().__init__()
        self.year = year
        self.month = month
        self.data_list = data_list
        self.cell_size = cell_size
        self.spacing = spacing
        self.setHandlesChildEvents(False)
        self.build()

    def build(self):
        first_weekday, days_in_month = monthrange(self.year, self.month)
        first_weekday = (first_weekday + 1) % 7
        date = QDate(self.year, self.month, 1)
        # 添加月份标题
        is_dark = QApplication.palette().color(QPalette.Window).value() < 128
        text_color = QColor("white") if is_dark else QColor("black")
        title = QGraphicsSimpleTextItem(date.toString("MMMM"))
        title.setBrush(QBrush(text_color))
        title.setPos(0, 0)
        self.addToGroup(title)
        self.title_height = self.cell_size * 2
        # 添加每日格
        row = 0
        col = first_weekday

        for day in range(1, days_in_month + 1):
            d = QDate(self.year, self.month, day)
            count = self.data_list.get(d.toString("yyyy-MM-dd"), 0)

            x = col * (self.cell_size + self.spacing)
            y = self.title_height + row * (self.cell_size + self.spacing)
            rect = QRectF(x, y, self.cell_size, self.cell_size)

            item = DayItem(d, count, rect)
            item.setParentItem(self)

            col += 1
            if col == 7:
                col = 0
                row += 1

class YearHeatMapView(QWidget):
    def __init__(self, year:int):
        super().__init__()
        self.year = year
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.view.setMouseTracking(True)
        self.view.viewport().setMouseTracking(True)

        # === 顶部导航栏 ===
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.clicked.connect(self.goto_prev_year)

        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.clicked.connect(self.goto_next_year)

        self.year_label = QLabel(str(self.year))
        self.year_label.setAlignment(Qt.AlignCenter)
        self.year_label.setFixedHeight(30)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 5, 10, 5)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.year_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)

        # === 总体布局 ===
        main_layout = QVBoxLayout()
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.view)
        self.setLayout(main_layout)

        self.data = {}
        self.get_data()
        self.build_scene()

    def refresh(self,year:int):
        self.year = year
        self.get_data()
        self.build_scene()

    def get_data(self):
        tmp_data:list[BaseEvent] = []
        for i in range(1,13):
            tmp_data.extend(EventSQLManager.get_events_in_month(self.year,i))
        for event in tmp_data:
            self.data.setdefault(event.datetime[:10],0) 
            self.data[event.datetime[:10]] += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.build_scene()

    def build_scene(self):
        self.scene.clear()

        total_columns = 4
        total_rows = 3
        view_width = self.view.viewport().width()
        view_height = self.view.viewport().height()
        base_spacing = min(view_width, view_height) / 10
        spacing = max(8, base_spacing)  # 间距


        # 动态计算单元格尺寸
        month_block_width = (view_width - (total_columns - 1) * spacing) / total_columns
        month_block_height = (view_height - (total_rows - 1) * spacing) / total_rows

        # 计算 cell_size（按列/行最小值）
        cell_width = month_block_width / 7
        cell_height = (month_block_height - 20) / 6  # 20: 预留标题高度
        cell_size = min(cell_width, cell_height)

        for i in range(12):
            row = i // 4
            col = i % 4
            month = i + 1

            block = MonthBlock(self.year, month, self.data,cell_size=cell_size,spacing=2)
            x = col * (cell_size * 7 + spacing)
            y = row * (cell_size * 6 + 20 + spacing)
            block.setPos(x, y)
            self.scene.addItem(block)

        self.scene.setSceneRect(self.scene.itemsBoundingRect())

    def goto_prev_year(self):
        self.year -= 1
        self.year_label.setText(str(self.year))
        self.refresh(self.year)

    def goto_next_year(self):
        self.year += 1
        self.year_label.setText(str(self.year))
        self.refresh(self.year)