from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardRemove


# забираем переменные типов тренирвоки и всё что с ней связано
from training import *


def menu_builder(buttons_text: list, width: int) -> ReplyKeyboardBuilder:
	builder = ReplyKeyboardBuilder()
	builder.row(*[KeyboardButton(text=btn) for btn in buttons_text], width=width)
	return builder


buttons_block_text = [block.value for block in BLOCKS_MAPPING]
buttons_type_text = [f'Тип: {type_}' for type_ in ('Варианты', 'Блоки', 'Задания')]
buttons_exercise_text = [f'Задание {i}' for i in range(1, 21)]

choose_block_builder = menu_builder(buttons_block_text, width=2)
button_exercise_builder = menu_builder(buttons_exercise_text, width=4)
choose_type_builder = menu_builder(buttons_type_text, width=4)

SIGNUP_TEXT = "Мы с вами не знакомы, нажмите /start"
