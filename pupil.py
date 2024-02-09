from aiogram.types import Message
from dataclasses import dataclass, asdict

# забираем переменные базы данных
from database import *


@dataclass
class Pupil:
	pid: int  # id ученика
	all_tried: int = 0  # кол-во попыток
	success: int = 0
	current_type: str = None
	task: list = (None, None)
	topic: int = None
	block: str = None
	variant: list = None
	variant_index_topic: int = 0
	variant_success: int = 0

	def as_dict(self) -> dict:
		# представление данных в виде словаря ключ значение
		return asdict(self)


def get_pupil(message: Message) -> dict:
	pid = message.from_user.id
	return pupils_table.find_one({'pid': pid})


def clear_train_type(pid):
	update_pupil_data(pid, field='current_type', value=None)
	update_pupil_data(pid, field='task', value=[None, None])
	update_pupil_data(pid, field='topic', value=None)
	update_pupil_data(pid, field='block', value=None)
	update_pupil_data(pid, field='variant', value=None)
	update_pupil_data(pid, field='variant_index_topic', value=0)
	update_pupil_data(pid, field='variant_success', value=0)


def clear_all(pid):
	update_pupil_data(pid, field='all_tried', value=0)
	update_pupil_data(pid, field='success', value=0)
	clear_train_type(pid)
