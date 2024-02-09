import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command

# забираем переменные для создании меню
from menu import *
# забираем переменные для создании тренировки
from training import *

logging.basicConfig(level=logging.INFO)

bot_token = 'тут должен быть токен бота'
bot = Bot(token=bot_token)
dp = Dispatcher()

# обработчик команды старт
@dp.message(CommandStart())
async def start(message: Message):
	#
	pupil = get_pupil(message)
	if pupil:
		return await message.answer(text="Мы уже с вами знакомы!")
	else:
		# регистрация ученика
		pid = message.from_user.id
		pupil = Pupil(pid)
		pupils_table.insert_one({'pid': pid, **pupil.as_dict()})
		logging.info(f"added new pupil {pupil}")
		return await message.answer(
			text="Привет! Я - бот, который поможет вам в решении тестовой части ЕГЭ по русскому языку.\n"
			     "Вы можете решать заданя по вариантам, по блокам или по их порядковым номерам в КИМе.\n"
			     "Нажмите /practice, чтобы перейти к практике")


@dp.message(Command(commands=['practice']))
async def practice(message: Message):
	# находим ученика, и если его нет - отправляем на регистрацию
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	# проверяем, есть ли незавершённые задачи
	topic_index, task_index = pupil.get('task')
	if topic_index is not None:
		await message.answer(text="У вас есть нерешенная задача")
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return
	# создаем меню выбора типа обучения
	await message.answer(
		text="Выберите тип задания",
		reply_markup=choose_type_builder.as_markup(resize_keyboard=True)
	)

# команда для выдачи ученику статистики решенных задач
@dp.message(Command(commands=['stat']))
async def stat(message: Message):
	# находим ученика, и если его нет - отправляем на регистрацию
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	# выводим статистику
	if pupil.get('all_tried'):
		logging.info(f"send stats to {pupil}")
		await message.answer(text=f"Вы решили {pupil.get('all_tried')} заданий\n"
		                          f"Из них верно {pupil.get('success')} заданий\n"
		                          f"Это {(pupil.get('success') / pupil.get('all_tried')) * 100:.1f}%")
	else:
		logging.info(f"0 tasks was done by {pupil.get('pid')}")
		await message.answer(text="Вы еще не решили ни одного задания.\n"
		                          "Кажется, пора начать.\n"
		                          "Может приступим? Нажмите /practice")


# обработчик команды для очистки статистики ученика
@dp.message(Command(commands=['clear']))
async def clear_stat(message: Message):
	# находим ученика, и если его нет - отправляем на регистрацию
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	# очищаем статистику
	pid = pupil.get('pid')
	clear_all(pid)
	logging.info(f"stat removed for {pid}")
	await message.answer(text="Вся статистика была сброшена.\n"
	                          "Решили начать с чистого листа?\n"
	                          "Нажмите /practice")

# обработчик команды для прерывания тренировки
@dp.message(Command(commands=['stop']))
async def stop_doing_task(message: Message):
	# находим ученика, и если его нет - отправляем на регистрацию
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	# очищаем тип обучения и текущие задачи
	pid = pupil.get('pid')
	clear_train_type(pid)
	logging.info(f"train removed for {pid}")
	await message.answer(text="Вы остановили тренировку\n"
	                          "Жми /practice")


# выбор метода решения задач
@dp.message(lambda x: x.text in buttons_type_text)
async def choose_train_type(message: Message):
	# находим ученика, и если его нет - отправляем на регистрацию
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	# получаем текущую задачу ученика
	pid = pupil.get('pid')
	topic_index, task_index = pupil.get('task')
	# если она есть, нужно дорешать или остановиться
	if topic_index is not None:
		await message.answer(text="У вас есть нерешенная задача.")
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return
	#
	current_type = TrainType(message.text.replace('Тип: ', ''))
	# сохраняем выбор ученика
	update_pupil_data(pid, field='current_type', value=current_type.value)
	logging.info(f'added type to {pid}')

	match current_type:
		# выбор блока заданий
		case TrainType.BLOCK:
			await message.answer(
				text="Выберите блок заданий",
				reply_markup=choose_block_builder.as_markup(resize_keyboard=True)
			)
		# уведомление о генерации варианта
		case TrainType.VARIANT:
			await message.answer(text="Вам сгенерирован вариант")
			logging.info(f"variant was generated for {pid}")
			# сохранение варианта, который был сгенерирован для ученика
			topic_index, task_index = generate_task(pid)
			await message.answer(text=form_task_text(topic_index, task_index),
			                     reply_markup=ReplyKeyboardRemove(),
			                     parse_mode=ParseMode.HTML)
		# выбор задания (по нумерации в КИМе)
		case TrainType.TASK:
			await message.answer(
				text="Выберите задания",
				reply_markup=button_exercise_builder.as_markup(resize_keyboard=True)
			)

# выбор блока задач (если ученик ранее выбрал "блок")
@dp.message(lambda x: x.text in buttons_block_text)
async def choosed_block(message: Message):
	# находим ученика, и если его нет - отправляем на регистрацию
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	pid = pupil.get('pid')
	topic_index, task_index = pupil.get('task')
	# находим текущую задачу, если она есть, нужно дорешать или остановиться
	if topic_index is not None:
		await message.answer(text="У вас есть нерешенная задача")
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return

	if not pupil.get('current_type'):
		return

	update_pupil_data(pid, 'block', Blocks(message.text).value)

	logging.info(f"added block to {pid}")
	# генерируем задачу для ученика
	topic_index, task_index = generate_task(pid)
	logging.info(f"added random task from block to {pid}")

	await message.answer(text=form_task_text(topic_index, task_index),
	                     reply_markup=ReplyKeyboardRemove(),
	                     parse_mode=ParseMode.HTML)


# выбор задания (если ученик ранее выбрал решение задач по номерам в КИМе)
@dp.message(lambda x: x.text in buttons_exercise_text)
async def choosed_task(message: Message):
	# находим ученика, и если его нет - отправляем на регистрацию
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	pid = pupil.get('pid')
	topic_index, task_index = pupil.get('task')
	# находим текущую задачу, если она есть, нужно дорешать или остановиться
	if topic_index is not None:
		await message.answer(text="У вас есть нерешенная задача.")
		await message.answer(text=form_task_text(topic_index, task_index),
		                     reply_markup=ReplyKeyboardRemove(),
		                     parse_mode=ParseMode.HTML)
		return
	if not pupil.get('current_type'):
		return

	topic_index = int(message.text.replace('Задание ', ''))
	update_pupil_data(pid, 'topic', topic_index)
	# выдача ученику задания на основе его выбора
	topic_index, task_index = generate_task(pid)

	await message.answer(text=form_task_text(topic_index, task_index),
	                     reply_markup=ReplyKeyboardRemove(),
	                     parse_mode=ParseMode.HTML)

# функция проверки ответа ученика -> выдача нового задания
@dp.message(lambda x: x.text)
async def check_answer(message: Message):
	# получаем ответ ученика
	pupil_answer = message.text.lower()
	pupil = get_pupil(message)
	if not pupil:
		return await message.answer(text=SIGNUP_TEXT)
	pid = pupil.get('pid')
	# проверка выбора темы, если ее нет, то сообщаем ученику об этом
	if not any((pupil.get('task')[0], pupil.get('block'), pupil.get('variant'))):
		logging.info(f"didn't find the topic")
		return await message.answer(text="Вы не выбрали тип решения задач.\n"
		                                 "Нажмите /practice")
	# если тема есть, то достаем ответ на него из бд
	topic_index, task_index = pupil.get('task')
	task = list(tasks_table.find({'topic': topic_index}))[task_index]
	# проверяем ответ на правильность, добавляем задание в статистику
	if pupil_answer in task.get('answer'):
		update_pupil_data(pid, 'success', 1, increment=True)
		if pupil.get('variant'):
			update_pupil_data(pid, 'variant_success', 1, increment=True)
		await message.answer(text=form_answer_text(task, correct=True),
		                     parse_mode=ParseMode.HTML)
	else:
		await message.answer(text=form_answer_text(task, correct=False),
		                     parse_mode=ParseMode.HTML)
	# добавляем ответ в общую статистику ученика
	update_pupil_data(pid, field='all_tried', value=1, increment=True)

	# если ученик выбрал решать вариант, то отправляем ему следующую задачу
	# если ученик закончил решать вариант, то уведомляем его об этом. выводим статискику решенных заданий для варианта
	topic_index, task_index = generate_task(pid)
	if topic_index is None:  # and pupil.current_type == TrainType.VARIANT:
		await message.answer(text=f"Вы закончили решение варианта.\n"
		                          f"Верно решено {pupil.get('variant_success')} из 20 заданий\n",
		                     parse_mode=ParseMode.HTML)
		# сброс типа обучения
		logging.info(f"{pid} finished variant")
		update_pupil_data(pid, 'variant_success', 0)
		clear_train_type(pid)
		return

	return await message.answer(text=form_task_text(topic_index, task_index),
	                            parse_mode=ParseMode.HTML)


if __name__ == '__main__':
	dp.run_polling(bot)
