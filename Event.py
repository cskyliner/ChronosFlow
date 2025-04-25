import os
import sqlite3
BASE_DIR = os.path.dirname(__file__)
#TODO:前端提供路径接口，处理文件存储位置问题
DB_PATH = os.path.join(BASE_DIR, "local_data/events.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print("数据库路径:", DB_PATH)
TYPE_MAP = {
    "title": "TEXT",
    "date": "TEXT",
    "notes": "TEXT",
    "done": "INTEGER",
    "advance_time": "INTEGER",
    "tags": "TEXT",
}
TABLE_MAP = {
    "ddlevents": "DDL",
    "taskevents": "Task",
    "clockevents": "Clock",
}

def create_table_if_not_exist(table_name:str,data)->None:
    """
    根据输入表名创建新表TODO: tag的三表多对多查询机制
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

    def to_dict(self):
        raise NotImplementedError

    def table_name(self):
        """
        给出该类对应表名
        """
        return self.__class__.__name__.lower()+'s'

    def add_event(self):
        """
        将Event加入日程中，若已经存在于table中则跳过
        """
        if self.id is not None:
            raise RuntimeError("事件对象已有 ID，可能已经添加过数据库。")
        table_name = self.table_name() # 类名小写转换变复数作为table_name,注意是复数！！！
        data = self.to_dict()
        create_table_if_not_exist(table_name, data)
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data)) # 使用占位符防御SQL注入
        values = tuple(data.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        self.id = cursor.lastrowid # 获取table中的唯一id值
        conn.commit()

    def delete_event(self):
        """
        删除日程
        """
        table_name = self.table_name()
        query = f"DELETE FROM {table_name} WHERE id = ?"
        cursor.execute(query, (self.id,))
        conn.commit()

    def modify_event(self):
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
    输入：标题，截止时间，备注，是否完成，提前提醒时间
    """
    def __init__(self, title:str, date:str, notes:str, done:bool, advance_time:int):
        super().__init__(title)
        self.date = date
        self.notes = notes
        self.done = done
        self.advance_time = advance_time

    def to_dict(self):
        return {
            "title": self.title,
            "date": self.date,
            "notes": self.notes,
            "done": self.done,
            "advance_time": self.advance_time,
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
    registry = {
        "DDL": DDLEvent,
        "Task": TaskEvent,
        "Clock": ClockEvent
    }
    @classmethod
    def create(cls,event_type:str, **kwargs) -> BaseEvent:
        """
        根据种类创造不同Event
        :param event_type:
        :param kwargs:
        :return: BaseEvent
        """
        if event_type not in cls.registry:
            raise Exception(f"event_type {event_type} not supported")
        event_cls = cls.registry[event_type]
        return event_cls(**kwargs)
def search_all(keyword:str) -> list[BaseEvent]:
    """
    关键词全局搜索
    """
    result:list[BaseEvent] = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type ='table'") # 获取所有table
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})") # 通过PRAGMA获取table列信息
        columns_info = cursor.fetchall()
        columns_name = [column[1] for column in columns_info][1:]
        possible_columns = [column[1] for column in columns_info if "TEXT" == column[2]] # 排除格式非TEXT的列
        if not possible_columns:
            continue
        where_column = " OR ".join([f"{col} LIKE ?" for col in possible_columns])
        values = [f"%{keyword}%"]*len(possible_columns)
        query = f"SELECT * FROM {table} WHERE {where_column}" # 选择匹配关键字的行
        cursor.execute(query, values)
        rows = cursor.fetchall()
        for row in rows:
            paras = row[1:]
            kwargs = dict(zip(columns_name, paras)) # 将除了唯一id以外的参数传入工厂中，将数据转为类结构
            event = EventFactory.create(TABLE_MAP.get(table,"DDL"),**kwargs)
            event.id = row[0]
            result.append(event)
    return result