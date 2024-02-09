"""
Перменные для типов тренировки
"""
from enum import Enum
from random import randint

# забираем переменные базы данных
from pupil import *


class TrainType(Enum):
	BLOCK = 'Блоки'
	VARIANT = 'Варианты'
	TASK = 'Задания'


class Blocks(Enum):
	BLOCK_1 = "Работа с микротекстом"
	BLOCK_2 = "Языковые нормы"
	BLOCK_3 = "Орфография"
	BLOCK_4 = "Пунктуация"


BLOCKS_MAPPING: dict[Blocks, tuple] = {
	Blocks.BLOCK_1: (1, 3),
	Blocks.BLOCK_2: (4, 8),
	Blocks.BLOCK_3: (9, 15),
	Blocks.BLOCK_4: (16, 20),
}


def generate_task(pid: int) -> tuple:
	#
	pupil = pupils_table.find_one({'pid': pid})

	#
	current_type = TrainType(pupil.get('current_type'))

	topic_index, task_index = None, None

	match current_type:
		#
		case TrainType.BLOCK:
			current_block = Blocks(pupil.get('block'))
			topic_begin, topic_end = BLOCKS_MAPPING[current_block]
			topic_index = randint(topic_begin, topic_end)
			# берем данные из БД и случайно выбираем по топику
			tasks_count = tasks_table.count_documents({'topic': topic_index})
			task_index = randint(0, tasks_count - 1)
		#
		case TrainType.VARIANT:
			if not pupil.get('variant'):
				# генеируем вариант, в виде списка, где каждый элемент это номер задачи, а индекс элемента,
				variant = []
				for topic_index in range(1, 21):
					# узнаем сколько задач в топике
					tasks_count = tasks_table.count_documents({'topic': topic_index})
					# выбираем случайную задачу из топика, на основе их количества
					task_index = randint(0, tasks_count - 1)
					variant.append((topic_index, task_index))
				#
				update_pupil_data(pid, field='variant', value=variant)
				pupil['variant'] = variant
			if pupil.get('variant_index_topic') >= 20:
				return topic_index, task_index
			#
			variant_topic_index = pupil.get('variant_index_topic')
			topic_index, task_index = pupil.get('variant')[variant_topic_index]
			#
			update_pupil_data(pid, field='variant_index_topic', value=1, increment=True)
		#
		case TrainType.TASK:
			#
			topic_index = pupil.get('topic')
			tasks_count = tasks_table.count_documents({'topic': topic_index})
			task_index = randint(0, tasks_count - 1)

	update_pupil_data(pid, 'task', (topic_index, task_index))
	return topic_index, task_index


def form_task_text(topic_index: int, task_index: int) -> str:
	# находим эту задачу в базе данных и выдёргиваем поля
	task = list(tasks_table.find({'topic': topic_index}))[task_index]
	return (f"{task.get('instruction')}\n"
	        f"{task.get('text')}\n"
	        f"{task.get('task')}")


def form_answer_text(task: dict, correct: bool) -> str:
	answer = ['Верно!' if correct else 'Вы ошиблись( В следующий раз обязательно получится!',
	          f"Ответ: {task.get('answer')[0]}",
	          task.get("annotation")]
	return '\n'.join(answer)
