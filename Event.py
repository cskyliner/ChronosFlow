from common import *
import os
import sqlite3
from Emitter import Emitter

log = logging.getLogger(__name__)
# ===默认连接数据库（应该不会启用）===
DB_PATH = None
conn = None
cursor = None
latest_ddlevent = None
# ===数据名对应数据类型===
TYPE_MAP = {
	"title": "TEXT",
	"datetime": "DATETIME",
	"notes": "TEXT",
	"importance": "TEXT",
	"done": "INTEGER",
	"advance_time": "DATETIME",
	"tags": "TEXT",
}
TABLE_MAP = {
	"ddlevents": "DDL",
	"taskevents": "Task",
	"activityevents": "Activity",
}
# ===构建全局id===
def init_global_id_table():
	"""构建全局id表，包括唯一ID和创建时间"""
	cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_id (
            id INTEGER PRIMARY KEY,
			created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
	conn.commit()
def get_global_id()	-> int:
	"""获取全局id"""
	cursor.execute("INSERT INTO global_id DEFAULT VALUES")
	conn.commit()
	return cursor.lastrowid

def create_table_if_not_exist(table_name: str, data) -> None:
	"""
	根据输入表名和数据创建新表TODO: tag的三表多对多查询机制
	"""
	columns = ', '.join([f"{key} {TYPE_MAP.get(key, 'TEXT')}" for key in data.keys()])
	create_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            {columns})
    """
	cursor.execute(create_query)
	conn.commit()


class BaseEvent:
	"""
	事件基类
	"""

	def __init__(self, title: str):
		self.title = title
		self.id = None

	def to_dict(self) -> dict:
		raise NotImplementedError

	def table_name(self) -> str:
		"""
		给出该类对应表名,类名小写转换变**复数**
		"""
		return self.__class__.__name__.lower() + 's'

	def add_event(self) -> None:
		"""
		将Event加入日程中，若已经存在于table中则跳过
		"""
		if self.id is not None:
			raise RuntimeError("事件对象已有 ID，可能已经添加过数据库。")
		global_id = get_global_id() 					# 获取全局变量 
		table_name = self.table_name()
		data = self.to_dict()
		create_table_if_not_exist(table_name, data)
		columns = ', '.join(data.keys())
		placeholders = ', '.join(['?'] * len(data))  	# 使用占位符防御SQL注入
		values = tuple(data.values())
		query = f"INSERT INTO {table_name} (id,{columns}) VALUES (?,{placeholders})"
		cursor.execute(query, (global_id,) + values)
		self.id = global_id  							# 获取全局中的唯一id值作为事件标识符
		conn.commit()

	def delete_event(self) -> None:
		"""
		删除日程
		"""
		# 删除所在事件表记录
		table_name = self.table_name()
		query = f"DELETE FROM {table_name} WHERE id = ?"
		cursor.execute(query, (self.id,))
		# # 删除 global_id 表中的对应记录
		# query_global = "DELETE FROM global_id WHERE id = ?"
		# cursor.execute(query_global, (self.id,))
		conn.commit()

	def modify_event(self) -> None:
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
	输入：标题，截止时间，具体内容，提前提醒时间，重要程度，是否完成或过期（0为未完成，1为完成，2为过期）
	"""
	def __init__(self, title: str, datetime: str, notes: str, advance_time: str, importance: str, done: int = 0):
		super().__init__(title)
		self.datetime = datetime  # 格式："yyyy-MM-dd HH:mm"
		self.notes = notes
		self.advance_time = advance_time
		self.importance = importance
		self.done = done

	def to_dict(self) -> dict:
		return {
			"title": self.title,
			"datetime": self.datetime,
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


class ActivityEvent(BaseEvent):
	"""
	TODO:事件段时间
	"""

	def __init__(self, title):
		super().__init__(title)


class EventFactory:
	"""
	事件工厂
	"""
	registry: dict[str, BaseEvent] = {
		"DDL": DDLEvent,
		"Task": TaskEvent,
		"Clock": ActivityEvent
	}

	@classmethod
	def create(cls, event_type: str, add: bool, *args) -> DDLEvent:
		"""
		根据种类创造不同Event
		:param event_type:事件类型
		:param add:是否添加到数据库
		:param *args:参数
		:return: BaseEvent 事件类
		"""
		global latest_ddlevent
		if event_type not in cls.registry:
			raise Exception(f"event_type {event_type} not supported")
		event_cls = cls.registry[event_type]
		try:
			n_event: DDLEvent = event_cls(*args)
			if add is True:
				n_event.add_event()
				if n_event.table_name() == "ddlevents":
					now_time = QDateTime.currentDateTime()
					now_time = now_time.toString("yyyy-MM-dd HH:mm")
					log.info(f"now_time is {now_time}")
					if now_time > n_event.datetime:
						log.info(f"now_time is {now_time} 添加新事件比最新事件更晚，不更新最新事件")
					elif latest_ddlevent is None:
						log.info(f"没有最新的DDL事件，添加新事件:title：{n_event.title}; notes:{n_event.notes}")
						latest_ddlevent = n_event
						Emitter.instance().send_notice_signal((n_event,"create"))
						Emitter.instance().send_notice_signal((n_event,"create"))
					elif n_event.datetime < latest_ddlevent.datetime:
						log.info(f"添加新事件比最新事件更早，更新最新事件为新事件:title：{n_event.title}; notes:{n_event.notes}")
						latest_ddlevent = n_event
						Emitter.instance().send_notice_signal((n_event,"update"))
					else:
						log.info("添加新事件比最新事件更晚，不更新最新事件")
					log.info(f"add event {n_event.title} to {n_event.table_name()} table successfully")
			return n_event
		except TypeError as e:
			log.error(f"创建event失败，创建使用参数为{args}，Error:{e}")
			return None


def recieve_signal(recieve_data: tuple) -> None:
	"""
	接收信号函数
	"""
	global DB_PATH, conn, cursor  					# 全局变量
	if not recieve_data or len(recieve_data) == 0:
		log.error("接收信号失败，参数为空")
	elif recieve_data[0] == "create_event":
		event_type = recieve_data[1]  				# 事件类型
		add = recieve_data[2]  						# 是否添加到数据库
		args = recieve_data[3:]  					# 事件参数
		EventFactory.create(event_type, add, *args)
		log.info(f"接收{recieve_data[0]}信号成功，创建{event_type}事件，参数为{args}")
	elif recieve_data[0] == "modify_event":
		event_type = recieve_data[1]  				# 事件类型
		add = recieve_data[2]  						# 是否添加到数据库
		args = recieve_data[3:]  					# 事件参数
		event = EventFactory.create(event_type, add, *args)
		event.modify_event()
		log.info(f"接收{recieve_data[0]}信号成功，修改{event_type}事件，参数为{args}")
	elif recieve_data[0] == "storage_path":
		path = recieve_data[1]
		DB_PATH = os.path.join(path, "events.db")
		try:
			conn = sqlite3.connect(DB_PATH)
			cursor = conn.cursor()
			log.info(f"接收{recieve_data[0]}信号成功，存储路径为{path}")
			init_global_id_table()					# 如果没创建过全局id表就重新创建一个
		except Exception as e:
			log.error(f"连接数据库失败：{e}")
			QMessageBox.warning(
				None,
				"错误",
				"连接数据库失败，请检查存储路径是否正确",
			)
	elif recieve_data[0] == "delete_event":
		if cursor is not None and conn is not None:
			cursor.execute(f"DELETE FROM {recieve_data[1][1]} WHERE id = ?", (recieve_data[1][0],))
			conn.commit()
			log.info(f"删除{recieve_data[1][1]}中{recieve_data[1][0]}事件成功")
		else:
			log.error(f"未能连接到数据库，删除{recieve_data[1][1]}类{recieve_data[1][0]}事件失败")
	else:
		log.error(f"接收信号失败，未知信号类型{recieve_data[0]}，参数为{recieve_data[1:]}")


def request_signal(recieve_data: tuple) -> None:
	"""
	处理请求信号并回传数据
	"""
	result = ()
	signal_name = recieve_data[0]
	if signal_name == "search_all":
		keyword = recieve_data[1]
		result = search_all(keyword)
		log.info(f"接收{signal_name}请求信号成功，搜索事件{keyword}，搜索结果为{result}")
	elif signal_name == "update_upcoming":
		start_pos = recieve_data[1][0]
		event_num = recieve_data[1][1]
		result = get_data_time_order("ddlevents", start_pos, event_num)
		log.info(f"接收{signal_name}请求信号成功，获取事件")
	elif signal_name == "search_time":
		raise NotImplementedError("时间范围搜索功能尚未实现")
	elif signal_name == "search_some_columns":
		raise NotImplementedError("部分列搜索功能尚未实现")
	elif signal_name == "latest_event":
		now_time = recieve_data[1][0]
		result = get_latest_ddlevent(now_time)
		Emitter.instance().send_notice_signal((result,"get"))
		Emitter.instance().send_notice_signal((result,"get"))
		log.info(f"接收{signal_name}请求信号成功，获取事件")
		return
	else:
		if signal_name == "latest_event":
			print("纳尼？")
		log.error(f"接收信号失败，未知信号类型{signal_name}，参数为{recieve_data}")
	# 发送结果给回调函数
	Emitter.instance().send_backend_data_to_frontend_signal(result)

def get_latest_ddlevent(now_time:str) -> DDLEvent:
def get_latest_ddlevent(now_time:str) -> DDLEvent:
	"""
	获取最新的ddlevent，其 advance_time 不早于 now_time
	"""
	global latest_ddlevent
	log.info(f"当前时间：{now_time}")

	cursor.execute("SELECT * FROM ddlevents WHERE advance_time >= ? ORDER BY advance_time ASC LIMIT 1",
	log.info(f"当前时间：{now_time}")

	cursor.execute("SELECT * FROM ddlevents WHERE advance_time >= ? ORDER BY advance_time ASC LIMIT 1",
        			(now_time,))
	row = cursor.fetchone()
	if row is None:
		log.info("没有找到任何未来的DDL事件")
		return None
	paras = row[1:]
	event = EventFactory.create("DDL", False, *paras)
	event.id = row[0]
	log.info(f"获取最新的DDL事件id{event.id}成功，事件为{event.title} @ {event.advance_time}")
	latest_ddlevent = event
	return event

def search_all(keyword: tuple[str]) -> list[BaseEvent]:
	"""
	多关键词模糊性全局搜索（AND关系）
	"""
	result: list[BaseEvent] = []
	cursor.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name != 'global_id'")  					# 获取所有table
	tables = [row[0] for row in cursor.fetchall()]
	for table in tables:
		cursor.execute(f"PRAGMA table_info({table})")  										# 通过PRAGMA获取table列信息
		columns_info = cursor.fetchall()
		possible_columns = [column[1] for column in columns_info if "TEXT" == column[2]] 	# 排除格式非TEXT的列
		if not possible_columns:
			continue
		# 拼接语句，注意使用AND连接
		where_clauses = [
			" AND ".join(f"{col} LIKE ?" for key in keyword)
			for col in possible_columns
		]
		where_column = " OR ".join(where_clauses)  											# 选择所有匹配所有关键字的列
		values = [f"%{key}%" for key in keyword] * len(possible_columns)
		query = f"SELECT * FROM {table} WHERE {where_column}" 								# 选择匹配关键字的行
		cursor.execute(query, values)
		rows = cursor.fetchall()
		for row in rows:
			paras = row[1:]
			event = EventFactory.create(TABLE_MAP.get(table, "DDL"), False, *paras)
			event.id = row[0]
			result.append(event)
	return result


def search_time(start_time: str, end_time: str) -> list[BaseEvent]:
	"""
	时间范围搜索
	"""
	result: list[BaseEvent] = []
	cursor.execute("SELECT name FROM sqlite_master WHERE type ='table'")  	# 获取所有table名称
	tables = [row[0] for row in cursor.fetchall()]
	for table in tables:
		cursor.execute(f"PRAGMA table_info({table})")  						# 通过PRAGMA获取table列信息
		columns_info = cursor.fetchall()
		columns_name = [column[1] for column in columns_info][1:]
		if "datetime" not in columns_name:  								# 排除没有datetime列的table
			continue
		query = f"SELECT * FROM {table} WHERE datetime BETWEEN ? AND ?"
		cursor.execute(query, (start_time, end_time))
		rows = cursor.fetchall()
		for row in rows:
			paras = row[1:]
			event = EventFactory.create(TABLE_MAP.get(table, "DDL"), False, *paras)
			event.id = row[0]
			result.append(event)
	return result


def get_data_time_order(table_name: str, start_pos: int, event_num: int) -> tuple[BaseEvent]:
	'''
	从指定数据库中按时间顺序获取数据，从start_pos开始，取num个返回
	'''
	cursor.execute(f"SELECT name FROM sqlite_master WHERE type ='table'")  # 获取所有table名称
	tables = [row[0] for row in cursor.fetchall()]
	if table_name not in tables:
		log.error(f"{table_name}不存在")
		return ()
	query = f"SELECT * FROM {table_name} ORDER BY datetime DESC LIMIT {event_num} OFFSET {start_pos}"
	cursor.execute(query)
	rows = cursor.fetchall()
	log.info(f"获取数据成功，数据为{rows}")
	result = []
	for row in rows:
		paras = row[1:]
		event = EventFactory.create(TABLE_MAP.get(table_name, "DDL"), False, *paras)
		event.id = row[0]
		result.append(event)
	return tuple(result)
