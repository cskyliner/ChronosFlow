from datetime import datetime, timedelta
import logging
import json
log = logging.getLogger(__name__)

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
	
	def to_args(self) -> tuple:
		return (self.title, self.datetime, self.notes, self.advance_time, self.importance, self.done)

class TaskEvent(BaseEvent):
	"""
	TODO:分级任务管理
	"""

	def __init__(self, title):
		super().__init__(title)


class ActivityEvent(BaseEvent):
	"""
	日程类event
	输入：标题，每天开始时间，每天结束时间，开始日期，终止日期，笔记，重要程度，重复类型如("weekly"、"biweekly），重复具体星期
	"""

	def __init__(self, title:str, start_time:str, end_time:str, start_date:str, end_date:str, notes:str, importance:str = "Great",repeat_type:str = "不重复", repeat_days:tuple = []):
		super().__init__(title)
		self.start_time = start_time
		self.end_time = end_time
		self.start_date = start_date
		self.end_date = end_date
		self.notes = notes
		self.importance = importance
		self.repeat_type = repeat_type
		# 将多个星期tuple转为json存入数据库
		self.repeat_days = json.dumps(repeat_days) if repeat_type and len(repeat_type) > 0 else "[]"
		self.datetime = None

	def to_dict(self) -> dict:
		return {
			"title": self.title,
			"start_time": self.start_time,
			"end_time": self.end_time,
			"start_date" : self.start_date,
			"end_date": self.end_date,
			"notes": self.notes,
			"importance": self.importance,
			"repeat_type": self.repeat_type,
			"repeat_days": self.repeat_days,
		}
	
	def to_args(self) -> tuple:
		return (
			self.title,
			self.start_time,
			self.end_time,
			self.start_date,
			self.end_date,
			self.notes,
			self.importance,
			self.repeat_type,
			json.loads(self.repeat_days),
		)
	
	def expand(self, range_start:str, range_end:str) -> list[BaseEvent]:
		"""
		将重复日程扩展为多个单日日程
		"""
		# 转换为日期对象
		result = []
		start = datetime.strptime(range_start, "%Y-%m-%d").date()
		end = datetime.strptime(range_end, "%Y-%m-%d").date()
		base_start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
		base_end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
		repeat_days = json.loads(self.repeat_days)
		if start > base_end or end < base_start:
			log.error(f"{self.id} activity事件展开失败，起止日期错误")
			return result
		if self.repeat_type == "不重复":
			event = self._create_occurrence(base_start)
			result.append(event)
		elif self.repeat_type == "每周":
			current = max(start,base_start)
			while current <= min(end, base_end):
				if self._is_valid_recurrence_day(current, repeat_days):
					result.append(self._create_occurrence(current))
				current += timedelta(days=1)
		elif self.repeat_type == "每两周":
			current = max(start,base_start)
			while current <= min(end, base_end):
				delta_days = (current - base_start).days
				week_index = delta_days // 7
				if week_index % 2 == 0 and self._is_valid_recurrence_day(current, repeat_days):
					result.append(self._create_occurrence(current))
				current += timedelta(days=1)
		else:
			log.error(f"错误的重复类型，无法展开{self.id} activity事件")
		return result


	def _create_occurrence(self, date_obj:datetime) -> "ActivityEvent":
		"""
		创建子日程
		"""
		occ = ActivityEvent(
				self.title,
				self.start_time,
				self.end_time,
				self.start_date,
				self.end_date,
				self.notes,
				self.importance,
				self.repeat_type,
				json.loads(self.repeat_days)	
		)
		# 记录原始id，便于后续从扩张出的事件中修改原重复事件
		occ.id = self.id
		# 记录某天发生的事件（开始时间），与ddl的datetime保持一致，方便复用
		occ.datetime =f"{date_obj.strftime('%Y-%m-%d')} {self.start_time}"
		return occ
	
	def _is_valid_recurrence_day(self, date_obj:datetime, repeat_days: list[str]) -> bool:
		"""
		判断某天是否为重复事件之一
		"""
		weekday_map = {
		0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu",
		4: "Fri", 5: "Sat", 6: "Sun"
		}
		weekday_str = weekday_map[date_obj.weekday()]
		return weekday_str in repeat_days
	
