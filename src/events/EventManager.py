import logging
import os
import sqlite3
from calendar import monthrange
from common import *
from Emitter import Emitter
from events.Event import *
# from ioporter.course_importer import CourseScheduleImporter
import json

log = logging.getLogger(__name__)

class EventFactory:
	"""
	事件工厂
	"""
	registry: dict[str, BaseEvent] = {
		"DDL": DDLEvent,
		"Task": TaskEvent,
		"Activity": ActivityEvent
	}

	@classmethod
	def create(cls, id:int , event_type: str, add: bool, *args) -> BaseEvent:
		"""
		根据种类创造不同Event
		:params: id:事件ID event_type:事件类型 add:是否添加到数据库 *args:参数
		:return: BaseEvent 事件类
		"""
		if event_type not in cls.registry:
			raise Exception(f"EventFactory.create:event_type {event_type} not supported")
		event_cls = cls.registry[event_type]
		try:
			n_event: BaseEvent = event_cls(*args)
			if add is True and id is None:
				# 此时纯粹为创建新事件
				EventSQLManager.add_event(n_event)
				if isinstance(n_event,DDLEvent):
					# 如果是提醒类ddl，更新最新事件
					now_time = QDateTime.currentDateTime()
					now_time = now_time.toString("yyyy-MM-dd HH:mm")
					log.info(f"EventFactory.create:现在时间是 {now_time}")
					if now_time > n_event.datetime:
						log.info(f"EventFactory.create:现在时间是 {now_time} 添加新事件比最新事件更晚，不更新最新事件")
					elif EventSQLManager.latest_ddlevent is None:
						log.info(f"EventFactory.create:没有最新的DDL事件，添加新事件:title：{n_event.title}; notes:{n_event.notes}")
						EventSQLManager.latest_ddlevent = n_event
						Emitter.instance().send_notice_signal((n_event,"create"))
						Emitter.instance().send_notice_signal((n_event,"create"))
					elif n_event.datetime < EventSQLManager.latest_ddlevent.datetime:
						log.info(f"EventFactory.create:添加新事件比最新事件更早，更新最新事件为新事件:title：{n_event.title}; notes:{n_event.notes}")
						EventSQLManager.latest_ddlevent = n_event
						Emitter.instance().send_notice_signal((n_event,"update"))
					else:
						log.info("EventFactory.create:添加新事件比最新事件更晚，不更新最新事件")
					log.info(f"EventFactory.create:成功添加 {n_event.title} 到 {n_event.table_name()} 表中")
			elif id is not None:
				# 此时返回有id的事件，相当于根据id找出原事件
				n_event.id = id
			return n_event
		except TypeError as e:
			log.error(f"EventFactory.create:创建event失败，创建使用参数为{args}，Error:{e}")
			return None
		
class EventSQLManager:
	# ===默认连接数据库（应该不会启用）===
	DB_PATH = None
	conn = None
	cursor = None
	latest_ddlevent = None
	# 字段类型映射表：用于根据字段名自动生成 SQL 建表语句
	TYPE_MAP:dict = {
		"title": "TEXT",              # 事件标题
		"datetime": "DATETIME",       # 截止时间或触发时间
		"notes": "TEXT",              # 备注信息
		"importance": "TEXT",         # 重要程度
		"done": "INTEGER",            # 完成状态（0未完成/1完成/2过期）
		"advance_time": "DATETIME",   # 提前提醒时间
		"tags": "TEXT",               # 标签信息（预留）
		"start_time": "TEXT",         # 开始时间（如09:00）
		"end_time": "TEXT",           # 结束时间（如10:00）
		"start_date": "TEXT",         # 起始日期（如2025-06-01）
		"end_date": "TEXT",			  # 终止日期（如2025-06-02）
		"repeat_type": "TEXT",        # 重复类型（如"weekly"）
		"repeat_days": "TEXT",        # 重复的周几（JSON字符串，例如["Mon", "Wed"]）
	}
	TABLE_MAP:dict = {
		"ddlevents": "DDL",
		"taskevents": "Task",
		"activityevents": "Activity",
	}
	# === 初始化数据库连接 ===
	@classmethod
	def init_connection(cls, db_path: str):
		"""初始化数据库连接"""
		cls.DB_PATH = db_path
		cls.conn = sqlite3.connect(db_path)
		cls.cursor = cls.conn.cursor()
		# 未创建全局id表就新创建一个
		cls.init_global_id_table()
		# 更新最新事件
		now_time = QDateTime.currentDateTime()
		now_time = now_time.toString("yyyy-MM-dd HH:mm")
		cls.latest_ddlevent = cls.get_latest_ddlevent(now_time)
		log.info(f"数据库初始化成功，最新ddl事件：{cls.latest_ddlevent.title}")

	# ===管理全局id表===
	@classmethod
	def init_global_id_table(cls):
		"""如果没有，就构建全局id表，包括唯一ID和创建时间"""
		cls.cursor.execute("""
			CREATE TABLE IF NOT EXISTS global_id (
				id INTEGER PRIMARY KEY,
				created_at TEXT DEFAULT (datetime('now', 'localtime'))
			)
		""")
		cls.conn.commit()

	@classmethod
	def get_global_id(cls)	-> int:
		"""获取全局id"""
		cls.cursor.execute("INSERT INTO global_id DEFAULT VALUES")
		cls.conn.commit()
		return cls.cursor.lastrowid
	
	# 对表操作
	@classmethod
	def create_table_if_not_exist(cls, table_name: str, data) -> None:
		"""
		根据输入表名和数据创建新表TODO: tag的三表多对多查询机制
		"""
		columns = ', '.join([f"{key} {cls.TYPE_MAP.get(key, 'TEXT')}" for key in data.keys()])
		create_query = f"""
			CREATE TABLE IF NOT EXISTS {table_name} (
				id INTEGER PRIMARY KEY,
				{columns})
		"""
		cls.cursor.execute(create_query)
		cls.conn.commit()

	@classmethod
	def get_latest_ddlevent(cls, now_time:str) -> DDLEvent:
		"""
		获取最新的ddlevent，其 advance_time 不早于 now_time
		"""
		log.info(f"当前时间：{now_time}")

		cls.cursor.execute("SELECT * FROM ddlevents WHERE advance_time >= ? ORDER BY advance_time ASC LIMIT 1",
						(now_time,))
		row = cls.cursor.fetchone()
		if row is None:
			log.info("get_latest_ddlevent:没有找到任何未来的DDL事件")
			return None
		paras = row[1:]
		event = EventFactory.create(None, "DDL", False, *paras)
		event.id = row[0]
		log.info(f"get_latest_ddlevent:获取最新的DDL事件成功，事件为{event.title} @ {event.advance_time}")
		cls.latest_ddlevent = event
		return event
	
	@classmethod
	def get_month_range_str(cls, year: int, month: int):
		"""
		获得该月的起止日期
		"""
		first_day = f"{year:04d}-{month:02d}-01"
		last_day = f"{year:04d}-{month:02d}-{monthrange(year, month)[1]:02d}"
		return first_day, last_day
	
	@classmethod
	def get_events_in_month(cls, year: int, month: int) -> list[BaseEvent]:
		"""
		获取指定年份和月份的所有事件（ddl基于 datetime 字段匹配年月,activity 先判断起止日期是否落入月份，其次如果是重复事件则展开再进行筛选）。
		返回 BaseEvent 列表。
		"""
		# 验证输入
		if month < 1 or month > 12:
			log.warning(f"get_events_in_month:无效的月份输入: {month}")
			return []
		# 构造 SQL 查询：同时匹配年份和月份
		# 查询ddl
		ddl_query = """
			SELECT * FROM ddlevents 
			WHERE strftime('%Y', datetime) = ? 
			AND strftime('%m', datetime) = ?
			ORDER BY datetime ASC
		"""

		year_str = f"{year:04d}"  # 补零为4位（如 2024）
		month_str = f"{month:02d}"  # 补零为2位（如 07）
		# 查询activity
		first_day, last_day = cls.get_month_range_str(year,month)
		activity_query = f"""
			SELECT * FROM activityevents
			WHERE 
				(date(start_date) <= '{last_day}')
			AND (date(end_date) >= '{first_day}')
			ORDER BY date(start_date) ASC, time(start_time) ASC
		"""
		ddl_rows = []
		activity_rows = []
		try:
			cls.cursor.execute(ddl_query, (year_str, month_str))
			ddl_rows = cls.cursor.fetchall()
		except Exception as e:
			log.error(f"get_events_in_month:ddl_events数据库查询失败: {e}")
		try:
			cls.cursor.execute(activity_query)
			activity_rows = cls.cursor.fetchall()
		except Exception as e:
			log.error(f"get_events_in_month:activity_events数据库查询失败: {e}")
		events = []
		for row in ddl_rows:
			try:
				# 假设数据库字段顺序：id, title, advance_time, notes, ...
				paras = row[1:]  # 跳过 全局id 列
				event = EventFactory.create(None, "DDL", False, *paras)
				if event is not None and isinstance(event, DDLEvent):
					event.id = row[0]
					events.append(event)
					log.debug(f"get_events_in_month:加载ddl事件成功: {event.title} @ {event.datetime}-{event.advance_time}")
			except Exception as e:
				log.error(f"get_events_in_month:解析ddl事件失败（ID={row[0]}）: {e}")

		for row in activity_rows:
			try:
				paras = list(row[1:])
				# 此处微调bug，先将SQL中repeat_day的json形式还原为tuple再输入作为paras
				paras[-1] = json.loads(paras[-1])
				event:ActivityEvent = EventFactory.create(None, "Activity", False, *paras)
				if event is not None and isinstance(event, ActivityEvent):
					event.id = row[0]
					events += event.expand(first_day,last_day)
			except Exception as e:
				log.error(f"get_events_in_month:解析activity事件失败（ID={row[0]}）: {e}")

		log.info(f"get_events_in_month:找到 {len(events)} 个事件（{year}年{month}月）")
		return events
	
	@classmethod
	def get_events_between_twodays(cls, start_date:str, end_date:str) -> list[BaseEvent]:
		"""
		获取两个时间点之间的所有日程（暂时不加ddlevent)
		"""
		# 验证输入
		if start_date > end_date:
			log.warning(f"get_events_between_twodays:无效的起始日期输入: {start_date}-{end_date}")
			return []
		# 构造 SQL 查询：同时匹配年份和月份

		# 查询activity
		first_day, last_day = start_date,end_date
		activity_query = f"""
			SELECT * FROM activityevents
			WHERE 
				(date(start_date) <= '{last_day}')
			AND (date(end_date) >= '{first_day}')
			ORDER BY date(start_date) ASC, time(start_time) ASC
		"""
		activity_rows = []
		try:
			cls.cursor.execute(activity_query)
			activity_rows = cls.cursor.fetchall()
		except Exception as e:
			log.error(f"get_events_in_month:activity_events数据库查询失败: {e}")
		events = []

		for row in activity_rows:
			try:
				paras = list(row[1:])
				# 此处微调bug，先将SQL中repeat_day的json形式还原为tuple再输入作为paras
				paras[-1] = json.loads(paras[-1])
				event:ActivityEvent = EventFactory.create(None, "Activity", False, *paras)
				if event is not None and isinstance(event, ActivityEvent):
					event.id = row[0]
					events += event.expand(first_day,last_day)
			except Exception as e:
				log.error(f"get_events_in_month:解析activity事件失败（ID={row[0]}）: {e}")

		log.info(f"get_events_in_month:找到 {len(events)} 个事件（{start_date}-{end_date}）")
		return events
	
	@classmethod
	def get_specific_date_events(cls, table_name:str, date: QDate) -> list[BaseEvent]:
		'''
		从数据库中找到指定 QDate 当天的全部日程事件
		'''
		# 将 QDate 转换为 ISO 格式字符串（如 "2023-10-05"）
		target_date = date.toString("yyyy-MM-dd")
		# 查找对应表
		cls.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
		tables = [row[0] for row in cls.cursor.fetchall()]

		if table_name not in tables:
			log.error(f"事件表 {table_name} 不存在")
			return []
		# 查找指定时间的事件
		rows = []
		if table_name == "ddlevents":
			ddl_query = f"""
				SELECT * FROM {table_name}
				WHERE date(datetime) = ?
				ORDER BY datetime ASC
			"""
			cls.cursor.execute(ddl_query, (target_date,))
			rows = cls.cursor.fetchall()
		elif table_name == "activityevents":
			activity_query = f"""
				SELECT * FROM {table_name}
				WHERE (date(start_date) <= ?)
				AND (date(end_date) >= ?)
				ORDER BY start_time ASC 
			"""
			cls.cursor.execute(activity_query,(target_date,target_date))
			rows = cls.cursor.fetchall()
		else:
			log.error(f"{table_name}类事件未设置")

		log.info(f"get_specific_date_events:找到 {len(rows)} 条 {target_date} 的事件记录")

		# 转换为 BaseEvent 对象
		events = []
		if table_name == "ddlevents":
			for row in rows:
				event_id = row[0]
				paras = row[1:]
				event_type = "DDL"
				event:DDLEvent = EventFactory.create(event_id,event_type,False,*paras)
				events.append(event)
		elif table_name == "activityevents":
			for row in rows:
				event_id = row[0]
				paras = list(row[1:])
				# 此处微调bug，先将SQL中repeat_day的json形式还原为tuple再输入作为paras
				paras[-1] = json.loads(paras[-1])
				event_type = "Activity"
				event:ActivityEvent = EventFactory.create(event_id,event_type,False,*paras)
				result = event.expand(target_date,target_date)
				events += result
		else:
			log.error("get_specific_date_events:Event类型出错，类型未实现该函数")
		return events
	
	@classmethod
	def search_all(cls, keyword: tuple[str]) -> list[BaseEvent]:
		"""
		多关键词模糊性全局搜索（AND关系）,改为只搜索title和notes
		"""
		result: list[BaseEvent] = []
		cls.cursor.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name != 'global_id'")  					# 获取所有table
		tables = [row[0] for row in cls.cursor.fetchall()]
		for table in tables:
			cls.cursor.execute(f"PRAGMA table_info({table})")  									# 通过PRAGMA获取table列信息
			columns_info = cls.cursor.fetchall()
			possible_columns = [column[1] for column in columns_info if "TEXT" == column[2] and ("title" == column[1] or "notes" == column[1]) ] 	# 排除格式非TEXT的列
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
			cls.cursor.execute(query, values)
			rows = cls.cursor.fetchall()
			for row in rows:
				paras = list(row[1:])
				if cls.TABLE_MAP.get(table, "DDL") == "Activity":
					# 此处微调bug，先将SQL中repeat_day的json形式还原为tuple再输入作为paras
					paras[-1] = json.loads(paras[-1])		
				event = EventFactory.create(None, cls.TABLE_MAP.get(table, "DDL"), False, *paras)
				event.id = row[0]
				if isinstance(event, DDLEvent):
					result.append(event)
				elif isinstance(event, ActivityEvent):
					result += event.expand(event.start_date,event.end_date)
				else:
					log.error("search_all发生事件类型错误")
		return result
	
	@classmethod
	def search_time(cls, start_time: str, end_time: str) -> list[BaseEvent]:
		"""
		时间范围搜索
		"""
		result: list[BaseEvent] = []
		cls.cursor.execute("SELECT name FROM sqlite_master WHERE type ='table'")  	# 获取所有table名称
		tables = [row[0] for row in cls.cursor.fetchall()]
		for table in tables:
			cls.cursor.execute(f"PRAGMA table_info({table})")  						# 通过PRAGMA获取table列信息
			columns_info = cls.cursor.fetchall()
			columns_name = [column[1] for column in columns_info][1:]
			if "datetime" not in columns_name:  								# 排除没有datetime列的table
				continue
			query = f"SELECT * FROM {table} WHERE datetime BETWEEN ? AND ?"
			cls.cursor.execute(query, (start_time, end_time))
			rows = cls.cursor.fetchall()
			for row in rows:
				paras = row[1:]
				event = EventFactory.create(None, cls.TABLE_MAP.get(table, "DDL"), False, *paras)
				event.id = row[0]
				result.append(event)
		return result
	
	@classmethod
	def get_data_time_order(cls, table_name: str, start_pos: int, event_num: int) -> tuple[BaseEvent]:
		'''
		从指定数据库中按时间顺序获取ddl数据，从start_pos开始，取num个返回，目前暂时只支持ddlevent
		'''
		cls.cursor.execute(f"SELECT name FROM sqlite_master WHERE type ='table'")  # 获取所有table名称
		tables = [row[0] for row in cls.cursor.fetchall()]
		if table_name not in tables:
			log.error(f"{table_name}不存在")
			return ()
		if table_name == "ddlevents":
			query = f"SELECT * FROM {table_name} ORDER BY datetime ASC LIMIT {event_num} OFFSET {start_pos}"
		else:
			log.error("get_data_time_order:Event类型出错，类型未实现该函数")	
			return ()
		cls.cursor.execute(query)
		rows = cls.cursor.fetchall()
		log.info(f"获取数据成功，数据为{rows}")
		result = []
		for row in rows:
			paras = row[1:]
			event = EventFactory.create(None, cls.TABLE_MAP.get(table_name, "DDL"), False, *paras)
			event.id = row[0]
			result.append(event)
		return tuple(result)
	
	# 对特定事件进行操作，增删减改
	@classmethod
	def add_event(cls, event:BaseEvent) -> None:
		"""
		将Event加入日程中，若已经存在于table中则跳过
		"""
		if event.id is not None:
			# 证明已经存在过该事件，应该为修改事件
			log.error(f"已经存在过该事件，应该为修改事件")
			cls.modify_event(event)
		else:
			global_id = cls.get_global_id() 					# 获取全局变量 
			table_name = event.table_name()
			data = event.to_dict()
			cls.create_table_if_not_exist(table_name, data)
			columns = ', '.join(data.keys())
			placeholders = ', '.join(['?'] * len(data))  	# 使用占位符防御SQL注入
			values = tuple(data.values())
			query = f"INSERT INTO {table_name} (id,{columns}) VALUES (?,{placeholders})"
			cls.cursor.execute(query, (global_id,) + values)
			event.id = global_id  							# 获取全局中的唯一id值作为事件标识符
			cls.conn.commit()

	@classmethod
	def delete_event(cls, event:BaseEvent) -> None:
		"""
		删除日程
		"""
		# 删除所在事件表记录
		table_name = event.table_name()
		query = f"DELETE FROM {table_name} WHERE id = ?"
		cls.cursor.execute(query, (event.id,))
		# # 删除 global_id 表中的对应记录
		# query_global = "DELETE FROM global_id WHERE id = ?"
		# cursor.execute(query_global, (self.id,))
		cls.conn.commit()

	@classmethod
	def modify_event(cls, event:BaseEvent) -> None:
		"""
		修改日程
		"""
		log.info(f"修改事件{event.title}，事件ID为{event.id}")
		table_name = event.table_name()
		data = event.to_dict()
		columns = ', '.join([f"{k} = ?" for k in data.keys()])
		values = list(data.values()) + [event.id]
		query = f"UPDATE {table_name} SET {columns} WHERE id = ?"
		cls.cursor.execute(query, values)
		cls.conn.commit()
# ===统一管理接口===
def receive_signal(receive_data: tuple) -> None:
	"""
	接收信号函数
	"""
	global DB_PATH, conn, cursor, latest_ddlevent  	# 全局变量
	if not receive_data or len(receive_data) == 0:
		log.error("receive_signal:接收信号失败，参数为空")
	elif receive_data[0] == "create_event":
		log.info(f"receive_signal:接收{receive_data[0]}信号成功，创建{receive_data[1]}事件，参数为{receive_data[3:]}")
		event_type = receive_data[1]  				# 事件类型
		add = receive_data[2]  						# 是否添加到数据库
		args = receive_data[3:]  					# 事件参数
		EventFactory.create(None,event_type, add, *args)
	elif receive_data[0] == "modify_event":
		log.info(f"receive_signal:接收{receive_data[0]}信号成功，修改{receive_data[2]}事件，参数为{receive_data[3:]}")
		id = receive_data[1]  						# 事件ID
		event_type = receive_data[2]  				# 事件类型
		args = receive_data[3:]  					# 事件参数
		event = EventFactory.create(id, event_type,False, *args)
		EventSQLManager.modify_event(event)
		# 修改事件后需要更新最新事件
		now_time = QDateTime.currentDateTime()
		now_time = now_time.toString("yyyy-MM-dd HH:mm")
		result = EventSQLManager.get_latest_ddlevent(now_time)
		latest_ddlevent = result
		Emitter.instance().send_notice_signal((result,"update"))
	elif receive_data[0] == "storage_path":
		path = receive_data[1]
		DB_PATH = os.path.join(path, "events.db")
		try:
			log.info(f"receive_signal:接收{receive_data[0]}信号成功，存储路径为{path}")
			EventSQLManager.init_connection(DB_PATH)
		except Exception as e:
			log.error(f"receive_signal:连接数据库失败：{e}")
	elif receive_data[0] == "school_timetable_path":
		pass
	elif receive_data[0] == "delete_event":
		if EventSQLManager.cursor is not None and EventSQLManager.conn is not None:
			EventSQLManager.cursor.execute(f"DELETE FROM {receive_data[1][1]} WHERE id = ?", (receive_data[1][0],))
			EventSQLManager.conn.commit()
			log.info(f"receive_signal:删除{receive_data[1][1]}中{receive_data[1][0]}事件成功")
			# 删除事件后需要更新最新事件
			now_time = QDateTime.currentDateTime()
			now_time = now_time.toString("yyyy-MM-dd HH:mm")
			result = EventSQLManager.get_latest_ddlevent(now_time)
			latest_ddlevent = result
			if(receive_data[1][1] == "activityevents"):
				Emitter.instance().send_del_activity_event_signal()
			Emitter.instance().send_notice_signal((result,"update"))
		else:
			log.error(f"receive_signal:未能连接到数据库，删除{receive_data[1][1]}类{receive_data[1][0]}事件失败")
	else:
		log.error(f"receive_signal:接收信号失败，未知信号类型{receive_data[0]}，参数为{receive_data[1:]}")

def request_signal(recieve_data: tuple) -> None:
	"""
	处理请求信号并回传数据
	"""
	result = ()		# tuple便于信号传递
	signal_name = recieve_data[0]
	if signal_name == "search_all":
		keyword = recieve_data[1]
		result = EventSQLManager.search_all(keyword)
		log.info(f"request_signal:接收{signal_name}请求信号成功，搜索事件{keyword}，搜索结果为{result}")
	elif signal_name == "update_upcoming":
		start_pos = recieve_data[1][0]
		event_num = recieve_data[1][1]
		result = EventSQLManager.get_data_time_order("ddlevents", start_pos, event_num)
		log.info(f"request_signal:接收{signal_name}请求信号成功，获取事件")
	elif signal_name == "update_specific_date_upcoming":
		date = recieve_data[1][0]
		tmp = EventSQLManager.get_specific_date_events("ddlevents", date)
		tmp += EventSQLManager.get_specific_date_events("activityevents", date)
		result = tuple(tmp)
		log.info(f"request_signal:接收{signal_name}请求信号成功，获取事件")
	elif signal_name == "search_time":
		raise NotImplementedError("时间范围搜索功能尚未实现")
	elif signal_name == "search_some_columns":
		raise NotImplementedError("部分列搜索功能尚未实现")
	elif signal_name == "latest_event":
		now_time = recieve_data[1][0]
		result = EventSQLManager.get_latest_ddlevent(now_time)
		Emitter.instance().send_notice_signal((result,"get"))
		log.info(f"request_signal:接收{signal_name}请求信号成功，获取事件")
		# 此处不走统一回传信号通道，因此提前返回
		return
	else:
		log.error(f"request_signal:接收信号失败，未知信号类型{signal_name}，参数为{recieve_data}")
	# 发送结果给回调函数
	Emitter.instance().send_backend_data_to_frontend_signal(result)

