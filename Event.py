import sqlite3
conn = sqlite3.connect("/local_data/events.db")
cursor = conn.cursor()
class Event:
    def __init__(self, date, title, text=None):
        self.date = date
        self.title = title
        self.text = text
    def add_event(self):
        pass
    def delete_event(self):
        pass
    def modify_event(self):
        pass