from src.common import *
import os
from openai import OpenAI
from src.events.EventManager import EventSQLManager
from src.events.Event import *
from src.FontSetting import set_font

class LLMAssistantPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.api_key = os.getenv("OPENAI_API_KEY")

    def init_ui(self):
        self.setWindowTitle("AI 日程助手")
        layout = QVBoxLayout()

        date_edit_style = """
		        QDateEdit {
		            padding: 1px;
		            border: 1px solid #1E90FF;
		            border-radius: 4px;
		            background-color: transparent; 
		        }
		        QDateEdit:hover {
		            border-color: #24C1FF;
		        }
		    """
        calendar_style = """
		        QCalendarWidget QAbstractItemView:enabled {
		            color: palette(text);
		        }
		        QCalendarWidget QAbstractItemView:disabled {
		            color: palette(midlight);
		        }
		        QCalendarWidget QAbstractItemView:item:hover {
		            background-color: #e6f2ff;
		            color: #0066cc;
		        }
		        QCalendarWidget QToolButton {
		            font-size: 14px;
		            icon-size: 20px;
		        }
		    """

        self.date_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy年MM月dd日")
        self.start_date_edit.setStyleSheet(date_edit_style)
        set_font(self.start_date_edit)
        calendar = self.start_date_edit.calendarWidget()  
        calendar.setStyleSheet(calendar_style)
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy年MM月dd日")
        self.end_date_edit.setStyleSheet(date_edit_style)
        set_font(self.end_date_edit)
        calendar = self.end_date_edit.calendarWidget()
        calendar.setStyleSheet(calendar_style)
        self.end_date_edit.setDate(QDate.currentDate().addDays(7))
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.date_layout.addItem(spacer)
        label = QLabel("起始日期:")
        set_font(label)
        self.date_layout.addWidget(label)
        self.date_layout.addWidget(self.start_date_edit)
        self.date_layout.addItem(spacer)
        label = QLabel("结束日期:")
        set_font(label)
        self.date_layout.addWidget(label)
        self.date_layout.addWidget(self.end_date_edit)
        self.date_layout.addItem(spacer)
        layout.addLayout(self.date_layout)

        box_style = """
					QGroupBox {
						border: 1px solid palette(text);
						border-radius: 10px;
						margin-top: 1.5ex;
						padding: 1px;
					}
					QGroupBox::title {
						subcontrol-origin: margin;
						left: 10px;
						padding: 0 3px;
					}
					"""
        prompt_box = QGroupBox("Prompt 输入")
        set_font(prompt_box)
        prompt_box.setStyleSheet(box_style)
        prompt_layout=QVBoxLayout()
        prompt_box.setLayout(prompt_layout)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("请输入您的待规划事件及需求...")
        set_font(self.prompt_edit)
        prompt_layout.addWidget(self.prompt_edit)
        layout.addWidget(prompt_box)

        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        set_font(self.response_view)
        response_box = QGroupBox("LLM 回复")
        set_font(response_box)
        response_box.setStyleSheet(box_style)
        response_layout=QVBoxLayout()
        response_box.setLayout(response_layout)
        response_layout.addWidget(self.response_view)
        layout.addWidget(response_box)

        submit_btn = QPushButton("获取建议")
        set_font(submit_btn)
        submit_btn.setStyleSheet(
            """
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #1E90FF;
                    border-radius: 4px;
                    padding: 0px;
                    text-align: center;
                }
                QPushButton:hover {
                    border-color: #24C1FF; /*轻微高亮*/
                }
                QPushButton:pressed {
					background-color: #24C1FF;
				}
            """
        )
        submit_btn.setFixedSize(100, 40)
        submit_btn.clicked.connect(self.query_llm)
        layout.addWidget(submit_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def format_event(self,event: BaseEvent) -> str:
        if isinstance(event, DDLEvent):
            return f"[DDL] {event.title} 截止于 {event.datetime}，备注：{event.notes}，重要度：{event.importance}"
        elif isinstance(event, ActivityEvent):
            repeat_info = f"" if event.repeat_type != "不重复" else ""
            event.datetime
            return f"[日程] {event.title} 在 {event.datetime[:10]} {event.start_time}-{event.end_time}，备注：{event.notes}，重要度：{event.importance}{repeat_info}"
        else:
            return f"[其他] {event.title}"

    def build_prompt(self,events: list[BaseEvent], start_date: str, end_date: str, user_prompt: str) -> str:
        events_summary = "\n".join([self.format_event(e) for e in events])
        # 提示词可以优化
        return f"""你是一个智能日程助手，请根据以下已有的日程和DDL用户需求，生成合理的时间安排建议。

                时间范围：{start_date} 至 {end_date}

                已有事件：
                {events_summary}

                用户补充说明：
                {user_prompt}

                请给出简要的建议，包括冲突优化、重要任务提醒、时间规划建议等。"""

    def query_llm(self):
        prompt = self.prompt_edit.toPlainText().strip()
        if not self.api_key:
            QMessageBox.critical(self, "API Key Error", "OPENAI_API_KEY not set in environment variables.")
            return
        if not prompt:
            QMessageBox.warning(self, "输入错误", "Prompt 不能为空")
            return
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        events:list[BaseEvent] = EventSQLManager.get_events_between_twodays(start_date,end_date)
        full_prompt = self.build_prompt(events,start_date,end_date,prompt)
        log.info(f"用户需求为{full_prompt}")
        try:
            # 此处临时设置为deepseek，以后可以改进为其他模型，这里借鉴了deepseek官方文档(https://api-docs.deepseek.com/zh-cn/)
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            self.response_view.clear()

            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个智能时间管理助手，会根据用户的日程和DDL以及用户提出的需求，生成合理的日程规划"},
                    {"role": "user", "content": full_prompt}
                ],
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    new_text = chunk.choices[0].delta.content
                    self.response_view.insertPlainText(new_text)
                    QApplication.processEvents()
            log.info(f"AI建议为{self.response_view.toPlainText()}")
        except Exception as e:
            QMessageBox.critical(self, "API 错误", str(e))
