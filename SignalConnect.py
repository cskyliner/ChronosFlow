from Emitter import Emitter
from Event import recieve_signal
from common import logging

log = logging.getLogger(__name__)


def connect_event_signal():
	'''
	连接前后端信号
	'''
	try:
		Emitter.instance().create_event_signal.connect(recieve_signal)
		Emitter.instance().search_all_event_signal.connect(recieve_signal)
		Emitter.instance().search_some_columns_event_signal.connect(recieve_signal)
		log.info("成功连接创建事件信号")
	except Exception as e:
		log.error(f"连接信号失败，Error:{e}")
