import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Event import *

# '''测试添加事件
#     DDL类
#     输入：标题，截止时间，具体内容，提前提醒时间，重要程度，是否完成，
# '''
# test_event1 = DDLEvent("ai引论","2025-4-28 00:00","test","2025-4-27 00:00","重要",False)
# print(test_event1)
# def test_add_event():
#     test_event1.add_event()
# test_add_event()

# #===测试搜索到并删除事件===
# events = search_all("ai")
# for event in events:
#     print(event.title)
#     event.delete_event()
#     print(f"{event.id} event deleted")

#===重置测试库
def reset(table_name:str):
    """
    重置指定表的 AUTOINCREMENT 计数器，使下一次插入的记录 ID 从 1 开始。
    :param table_name: 表名
    """
    print(f"reset:{table_name}")
    create_query = f"""
        DELETE FROM sqlite_sequence WHERE name='{table_name}'
        """
    cursor.execute(create_query)
    conn.commit()
reset("ddlevents")
cursor.close()
conn.close()