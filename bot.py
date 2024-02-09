import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from dataclasses import dataclass, asdict

# забираем переменные для создании меню
from menu import *
from training import *

logging.basicConfig(level=logging.INFO)
bot_token = '6742804978:AAESNA7-XrAn6dXK64tzGE3tt5EtJzxkzRY'

bot = Bot(token=bot_token)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
	pupil = get_pupil(message)
	if pupil:
		return await message.answer(text="Мы уже с вами знакомы!")
	else:
		pid = message.from_user.id
		pupil = Pupil(pid)
		pupils_table.insert_one({'pid': pid, **asdict(pupil)})
		logging.info(f'added new user {pupil}')
		return await message.answer(
			text="Привет! Я - бот, который поможет вам в решении тестовой части ЕГЭ по русскому языку.\n"
			     "Вы можете решать заданя по вариантам, по блокам или по их порядковым номерам в КИМе.\n"
			     "Нажмите /try, чтобы перейти к практике.")

@dp.message(Command(commands=['try']))
async def practice(message: Message):
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)

	#
	topic_index, task_index = player.get('task')
	if topic_index is not None:
		await message.answer(text='У вас есть нерешенная задача.')
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return

	await message.answer(
		text='Выберите тип задания',
		reply_markup=choose_type_builder.as_markup(resize_keyboard=True)
	)


@dp.message(Command(commands=['stat']))
async def smd_stat(message: Message):
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)
	if player.get('all_tried'):
		logging.info(f"send stats to {player}")
		await message.answer(text=f"Вы решили {player.get('all_tried')} заданий\n"
		                          f"Из них верно {player.get('success')} заданий\n"
		                          f"Это {(player.get('success') / player.get('all_tried')) * 100:.1f}%")
	else:
		logging.info(f"0 tasks was done by {player.get('pid')}")
		await message.answer(text="Вы еще не решили ни одного задания.\n"
		                          "Кажется, пора начать.\n"
		                          "Может приступим? Нажмите /try")


@dp.message(Command(commands=['clear']))
async def clear_stat(message: Message):
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)
	pid = player.get('pid')
	#
	clear_all(pid)
	#
	logging.info(f'stat removed for {pid}')
	await message.answer(text="Вся статистика была сброшена.\n"
	                          "Решили начать с чистого листа?\n"
	                          "Нажмите /try")


@dp.message(Command(commands=['stop']))
async def stop_doing_task(message: Message):
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)
	#
	pid = player.get('pid')
	#
	clear_train_type(pid)
	#
	logging.info(f'train removed for {pid}')
	await message.answer(text="Вы остановили тренировку\n"
	                          "Жми /try")


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


@dp.message(lambda x: x.text in buttons_type_text)
async def choose_type(message: Message):
	#
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)
	pid = player.get('pid')
	topic_index, task_index = player.get('task')
	#
	if topic_index is not None:
		await message.answer(text="У вас есть нерешенная задача.")
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return

	current_type = TrainType(message.text.replace('Тип: ', ''))
	# сохраняем выбор пользователя
	update_value(pid, 'current_type', current_type.value)
	logging.info(f'added type to {pid}')

	match current_type:
		case TrainType.BLOCK:
			await message.answer(
				text="Выберите блок заданий",
				reply_markup=choose_block_builder.as_markup(resize_keyboard=True)
			)
		case TrainType.VARIANT:
			await message.answer(text="Вам сгенерирован вариант")
			logging.info(f"variant was generated for {pid}")

			topic_index, task_index = generate_task(pid)
			await message.answer(text=form_task_text(topic_index, task_index),
			                     reply_markup=ReplyKeyboardRemove(),
			                     parse_mode=ParseMode.HTML)
		case TrainType.TASK:
			await message.answer(
				text="Выберите задания",
				reply_markup=button_exercise_builder.as_markup(resize_keyboard=True)
			)


@dp.message(lambda x: x.text in buttons_block_text)
async def send_task_by_block(message: Message):
	#
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)
	pid = player.get('pid')
	topic_index, task_index = player.get('task')
	#
	if topic_index is not None:
		await message.answer(text="У вас есть нерешенная задача")
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return

	if not player.get('current_type'):
		return

	update_value(pid, 'block', Blocks(message.text).value)

	logging.info(f"added block to {pid}")
	# генерируем задачу для пользователя
	topic_index, task_index = generate_task(pid)
	logging.info(f"added random task from block to {pid}")

	await message.answer(text=form_task_text(topic_index, task_index),
	                     reply_markup=ReplyKeyboardRemove(),
	                     parse_mode=ParseMode.HTML)


@dp.message(lambda x: x.text in buttons_exercise_text)
async def send_task(message: Message):
	#
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)
	pid = player.get('pid')
	topic_index, task_index = player.get('task')
	#
	if topic_index is not None:
		await message.answer(text="У вас есть нерешенная задача.")
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return
	if not player.get('current_type'):
		return

	topic_index = int(message.text.replace('Задание ', ''))
	update_value(pid, 'topic', topic_index)
	#
	topic_index, task_index = generate_task(pid)

	await message.answer(text=form_task_text(topic_index, task_index),
	                     reply_markup=ReplyKeyboardRemove(),
	                     parse_mode=ParseMode.HTML)


@dp.message(lambda x: x.text)
async def check_ans(message: Message):
	user_answer = message.text.lower()
	player = get_pupil(message)
	if not player:
		return await message.answer(text=SIGNUP_TEXT)
	pid = player.get('pid')
	print(player)
	# fixme опасно хранить так в списке два элемента, можно нарваться на None как список
	if not any((player.get('task')[0], player.get('block'), player.get('variant'))):
		logging.info(f"didn't find the topic")
		return await message.answer(text="Вы не выбрали тип решения задач.\n"
		                                 "Нажмите /try")

	topic_index, task_index = player.get('task')
	task = list(tasks_table.find({'topic': topic_index}))[task_index]
	if user_answer in task.get('answer'):
		update_value(pid, 'success', 1, increment=True)
		if player.get('variant'):
			update_value(pid, 'variant_success', 1, increment=True)
		await message.answer(text=form_answer_text(task, correct=True),
		                     parse_mode=ParseMode.HTML)
	else:
		await message.answer(text=form_answer_text(task, correct=False),
		                     parse_mode=ParseMode.HTML)
	update_value(pid, 'all_tried', 1, increment=True)

	#
	topic_index, task_index = generate_task(pid)
	if topic_index is None:  # and player.current_type == TrainType.VARIANT:
		await message.answer(text=f"Вы закончили решение варианта.\n"
		                          f"Верно решено {player.get('variant_success')} из 20 заданий.\n",
		                     parse_mode=ParseMode.HTML)
		# сброс типа обучения
		logging.info(f"{pid} finished variant")
		update_value(pid, 'variant_success', 0)
		clear_train_type(pid)
		return

	return await message.answer(text=form_task_text(topic_index, task_index),
	                            parse_mode=ParseMode.HTML)


if __name__ == '__main__':
	dp.run_polling(bot)
