from PySide6.QtCore import QDate
from events.Event import *
from events.EventManager import *
import pandas as pd
import re
import logging
log = logging.getLogger(__name__)
class CourseScheduleImporter:
    in_path:str = None
    start_str:str = None
    semester_weeks:int = None
    week_map = {
        "星期一": "Mon",
        "星期二": "Tue",
        "星期三": "Wed",
        "星期四": "Thu",
        "星期五": "Fri",
        "星期六": "Sat",
        "星期日": "Sun",
    }
    time_start_map = {
        "第一节": "8:00",
        "第二节": "9:00",
        "第三节": "10:10",
        "第四节": "11:10",
        "第五节": "13:00",
        "第六节": "14:00",
        "第七节": "15:10",
        "第八节": "16:10",
        "第九节": "17:10",
        "第十节": "18:40",
        "第十一节": "19:40",
        "第十二节": "20:40",
    }
    time_end_map = {
        "第一节": "8:50",
        "第二节": "9:50",
        "第三节": "11:00",
        "第四节": "12:00",
        "第五节": "13:50",
        "第六节": "14:50",
        "第七节": "16:00",
        "第八节": "17:00",
        "第九节": "18:00",
        "第十节": "19:30",
        "第十一节": "20:30",
        "第十二节": "21:30",
    }
    @classmethod
    def init_importer(cls, in_path, start_str, semester_weeks):
        cls.in_path = in_path
        cls.start_str = start_str
        cls.semester_weeks = semester_weeks
    
    @classmethod
    def extract_info(cls):
        if cls.in_path.endswith(".xls"):
            schedule = pd.read_excel(cls.in_path, engine="xlrd", index_col=0)
        elif cls.in_path.endswith(".xlsx"):
            schedule = pd.read_excel(cls.in_path, engine="openpyxl", index_col=0)
        else:
            raise ValueError("不支持的文件格式")

        # 提取每一个单元格
        for idx, row in schedule.iterrows():
            for weekday in schedule.columns[1:]:
                cell = row[weekday]
                if pd.isna(cell):
                    continue
                else:
                    log.info(f"{weekday}，{idx}，内容：{cell}")
                    try:
                        # EventSQLManager.add_event(cls.process_data(cell,weekday,idx))
                        log.info(f"添加课程{cls.process_data(cell,weekday,idx).to_dict()}成功")
                    except Exception as e:
                        log.error(f"添加课程{cell}失败,{e}")
    @classmethod
    def process_data(cls, cell, weekday, idx) -> ActivityEvent:

        result:dict = {
            "title" : "",
            "location" : "",
            "remark" : "",
            "repeat_type" : "",
            "exam_info" : "",
        }
        # 搜索备注
        remark_match = re.search(r"[(（]备注：(.+?)[;；）)]",cell)
        if remark_match:
            result["remark"] = remark_match.group(1).strip()
        
        # 搜索上课地点
        all_brackets = re.findall(r"[（(]([^()（）]+)[)）]", cell)
        remark_start = re.search(r"[（(]备注", cell)
        if all_brackets and remark_start:
            # 获取在“备注”前面最近的一组括号内容作为上课地点
            location = ""
            for match in reversed(all_brackets):
                if cell.find(match) < remark_start.start():
                    location = match.strip()
                    break
            result["location"] = location
        # 搜索上课信息
        title_macth = re.search(r"(.+?)\s*[(（][^()]+[）)]\s*[(（]备注：",cell)
        if title_macth:
            result["title"] = title_macth.group(1).strip()
        # 搜索重复信息
        repeat_match = re.search(r"(每周|单周|双周)",cell)
        if repeat_match:
            result["repeat_type"] = repeat_match.group(1).strip()
        # 搜索考试信息
        exam_match = re.search(r"(考试(?:时间|方式)：[^；]+)",cell)
        if exam_match:
            result["exam_info"] = exam_match.group(1).strip()
        # 提取重复信息
        repeat_day = cls.week_map[weekday]
        start_time = cls.time_start_map[idx]
        end_time = cls.time_end_map[idx]
        repeat_type = None
        # 计算起止时间
        start_date_str = None
        start_date:QDate = QDate.fromString(cls.start_str, "yyyy-MM-dd")
        end_date = start_date.addDays(cls.semester_weeks*7 - 1)
        end_date_str = end_date.toString("yyyy-MM-dd")
        if result["repeat_type"] == "每周":
            repeat_type = "weekly"
            start_date_str = cls.start_str 
        elif result["repeat_type"] == "单周":
            repeat_type = "biweekly"
            start_date_str = cls.start_str
        elif result["repeat_type"] == "双周":
            repeat_type = "biweekly"
            start_date_str = start_date.addDays(7).toString("yyyy-MM-dd")
        else:
            log.error(f"{result['repeat_type']}，该重复类型未实现")
        # 合并notes
        notes = f"上课地点：{result['location']}\n备注：{result['remark']}\n{result['exam_info']}"
        """输入：标题，每天开始时间，每天结束时间，开始日期，终止日期，笔记，重要程度，重复类型如("weekly"、"biweekly），重复具体星期"""
        return EventFactory.create(None, "Activity", False, result["title"], start_time, end_time, start_date_str, end_date_str, notes, "Great", repeat_type, (repeat_day,))

# CourseScheduleImporter.init_importer("/Users/kylin/Desktop/timetable大一下.xls","2025-02-17",16)
# CourseScheduleImporter.extract_info() 