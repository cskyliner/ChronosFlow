from common import logging
import os
import sqlite3
from Emitter import Emitter
log = logging.getLogger(__name__)
#TODO:前端提供路径接口，处理文件存储位置问题，当前储存位置为根目录下local_data/events.db
#===连接数据库===
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "local_data/events.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print("数据库路径:", DB_PATH)
#===数据名对应数据类型===
TYPE_MAP = {
    "title": "TEXT",
    "datetime": "DATETIME",
    "notes": "TEXT",
    "importance":"TEXT",
    "done": "INTEGER",
    "advance_time": "DATETIME",
    "tags": "TEXT",
}
TABLE_MAP = {
    "ddlevents": "DDL",
    "taskevents": "Task",
    "clockevents": "Clock",
}

def create_table_if_not_exist(table_name:str,data)->None:
    """
    根据输入表名和数据创建新表TODO: tag的三表多对多查询机制
    """
    columns = ', '.join([f"{key} {TYPE_MAP.get(key,'TEXT')}" for key in data.keys()])
    create_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns})
    """
    cursor.execute(create_query)
    conn.commit()


class BaseEvent:
    """
    事件基类
    """
    def __init__(self, title:str):
        self.title = title
        self.id = None

    def to_dict(self)->dict:
        raise NotImplementedError

    def table_name(self)->str:
        """
        给出该类对应表名,类名小写转换变**复数**
        """
        return self.__class__.__name__.lower()+'s'

    def add_event(self)->None:
        """
        将Event加入日程中，若已经存在于table中则跳过
        """
        if self.id is not None:
            raise RuntimeError("事件对象已有 ID，可能已经添加过数据库。")
        table_name = self.table_name()
        data = self.to_dict()
        create_table_if_not_exist(table_name, data)
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data)) # 使用占位符防御SQL注入
        values = tuple(data.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        self.id = cursor.lastrowid # 获取table中的唯一id值
        conn.commit()

    def delete_event(self)->None:
        """
        删除日程
        """
        table_name = self.table_name()
        query = f"DELETE FROM {table_name} WHERE id = ?"
        cursor.execute(query, (self.id,))
        conn.commit()

    def modify_event(self)->None:
        """
        修改日程
        """
        table_name = self.table_name()
        data = self.to_dict()
        columns = ', '.join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [self.id]
        query = f"UPDATE {table_name} SET {columns} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()


class DDLEvent(BaseEvent):
    """
    DDL类
    输入：标题，截止时间，具体内容，提前提醒时间，重要程度，是否完成，
    """
    def __init__(self, title:str, datetime:str, notes:str, advance_time:str,importance:str,done:bool = False):
        super().__init__(title)
        self.date = datetime
        self.notes = notes
        self.advance_time = advance_time
        self.importance = importance
        self.done = done

    def to_dict(self)->dict:
        return {
            "title": self.title,
            "date": self.date,
            "notes": self.notes,
            "advance_time": self.advance_time,
            "importance": self.importance,
            "done": self.done,
        }


class TaskEvent(BaseEvent):
    """
    TODO:任务管理
    """
    def __init__(self, title):
        super().__init__(title)


class ClockEvent(BaseEvent):
    """
    TODO:打卡
    """
    def __init__(self, title):
        super().__init__(title)


class EventFactory:
    """
    事件工厂
    """
    registry:dict[str,BaseEvent] = {
        "DDL": DDLEvent,
        "Task": TaskEvent,
        "Clock": ClockEvent
    }
    @classmethod
    def create(cls,event_type:str,add:bool, *args) -> BaseEvent:
        """
        根据种类创造不同Event
        :param event_type:事件类型
        :param kwargs:参数
        :return: BaseEvent 事件类
        """
        if event_type not in cls.registry:
            raise Exception(f"event_type {event_type} not supported")
        event_cls = cls.registry[event_type]
        try:
            n_event:BaseEvent = event_cls(*args)
            log.info(f"create new event in {n_event.table_name()} table successfully")
            if add is True:
                n_event.add_event()
                log.info(f"add event {n_event.title} to {n_event.table_name()} table successfully")
            return n_event
        except TypeError as e:
            log.error(f"创建event失败，创建使用参数为{args}，Error:{e}")
            return None
        
def recieve_signal(recieve_data: tuple)-> None:
    """
    接收信号函数
    """
    if not recieve_data or len(recieve_data) == 0 :
        log.error("接收信号失败，参数为空")
    elif recieve_data[0] == "create_event":
        event_type = recieve_data[1] # 事件类型
        add = recieve_data[2] # 是否添加到数据库
        args = recieve_data[3:] # 事件参数
        EventFactory.create(event_type, add, *args)
        log.info(f"接收信号成功，创建事件{event_type}，参数为{args}")
    elif recieve_data[0] == "search_all":
        keyword = recieve_data[1]
        result = search_all(keyword)
        log.info(f"接收信号成功，搜索事件{keyword}，搜索结果为{result}")
        return result
        #sent_signal("search_all", result)
    else:
        log.error(f"接收信号失败，未知信号类型{recieve_data[0]}，参数为{recieve_data}")

def sent_signal(signal_name:str,emit_data: tuple)-> None:
    """
    发射信号回传数据
    """
    raise NotImplementedError("信号发射回传数据函数未实现")

def search_all(keyword:tuple[str]) -> list[BaseEvent]:
    """
    多关键词模糊性全局搜索（AND关系）
    """
    result:list[BaseEvent] = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type ='table'") # 获取所有table
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})") # 通过PRAGMA获取table列信息
        columns_info = cursor.fetchall()
        possible_columns = [column[1] for column in columns_info if "TEXT" == column[2]] # 排除格式非TEXT的列
        if not possible_columns:
            continue
        where_clauses = [
            " AND ".join(f"{col} LIKE ?" for key in keyword)
            for col in possible_columns
        ]
        where_column = " OR ".join(where_clauses)             # 选择所有匹配所有关键字的列
        values = [f"%{key}%" for key in keyword ]*len(possible_columns)
        query = f"SELECT * FROM {table} WHERE {where_column}" # 选择匹配关键字的行
        cursor.execute(query, values)
        rows = cursor.fetchall()
        for row in rows:
            paras = row[1:]
            event = EventFactory.create(TABLE_MAP.get(table,"DDL"),False,*paras)
            event.id = row[0]
            result.append(event)
    return result
def search_time(start_time:str,end_time:str) -> list[BaseEvent]:
    """
    时间范围搜索
    """
    result:list[BaseEvent] = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type ='table'") # 获取所有table名称
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})") # 通过PRAGMA获取table列信息
        columns_info = cursor.fetchall()
        columns_name = [column[1] for column in columns_info][1:]
        if "datetime" not in columns_name:  # 排除没有datetime列的table
            continue
        query = f"SELECT * FROM {table} WHERE datetime BETWEEN ? AND ?"
        cursor.execute(query, (start_time, end_time))
        rows = cursor.fetchall()
        for row in rows:
            paras = row[1:]
            event = EventFactory.create(TABLE_MAP.get(table,"DDL"),False,*paras)
            event.id = row[0]
            result.append(event)
    return result