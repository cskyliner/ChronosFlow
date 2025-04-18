import sqlite3
conn = sqlite3.connect("/local_data/events.db")
cursor = conn.cursor()

class BaseEvent:
    def __init__(self, date, title):
        self.date = date
        self.title = title
    def add_event(self):
        pass
    def delete_event(self):
        pass
    def modify_event(self):
        pass
class DDLEvent(BaseEvent):
    def __init__(self, date, title):
        super().__init__(date, title)
class TaskEvent(BaseEvent):
    def __init__(self, date, title):
        super().__init__(date, title)
class ReminderEvent(BaseEvent):
    def __init__(self, date, title):
        super().__init__(date, title)

class EventFactory:
    registry = {
        "DDL": DDLEvent,
        "Task": TaskEvent,
        "Reminder": ReminderEvent
    }
    @staticmethod
    def create(cls,event_type:str, **kwargs):
        if event_type not in cls.registry:
            raise Exception(f"event_type {event_type} not supported")
        event_cls = cls.registry[event_type]
        return event_cls(**kwargs)

