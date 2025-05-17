from Emitter import Emitter
from Event import receive_signal,request_signal
from common import logging
log = logging.getLogger(__name__)


def connect_event_signal():
	'''
	连接前后端信号
	'''
	try:
		Emitter.instance().create_event_signal.connect(receive_signal)
		Emitter.instance().search_all_event_signal.connect(request_signal)
		Emitter.instance().search_some_columns_event_signal.connect(request_signal)
		Emitter.instance().storage_path_signal.connect(receive_signal)
		Emitter.instance().search_time_event_signal.connect(request_signal)
		Emitter.instance().update_upcoming_event_signal.connect(request_signal)
		Emitter.instance().delete_event_signal.connect(receive_signal)
		Emitter.instance().modify_event_signal.connect(receive_signal)
		Emitter.instance().latest_event_signal.connect(request_signal)
		log.info("成功连接创建事件信号")
	except Exception as e:
		log.error(f"连接信号失败，Error:{e}")
