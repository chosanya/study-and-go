from aiogram import Bot, Dispatcher, F
from aiogram.filters import BaseFilter, Command, CommandStart
from aiogram.types import Message
import random


bot_token = '6742804978:AAESNA7-XrAn6dXK64tzGE3tt5EtJzxkzRY'
cmnds = ['start', 'help', 'stats', 'cancel']
admin_ids: list[int] = [173901673, 178876776, 197177271, 311155611]

bot = Bot(token=bot_token)
dp = Dispatcher()

class NumInMsg(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, list[int]]:
        numbers = []
        for word in message.text.split(' '):
            normalized_word = word.replace(',','').replace('.','').strip()
            if normalized_word.isdigit():
              numbers.append(int(normalized_word))
        if numbers:
            return {'numbers':numbers}
        return False

#@dp.message(start_filter)
#def start_filter(message: Message) -> bool:
 #   return message.text == '/start'

#@dp.message(start_filter)
#async def start_command(message: Message):
 #   await message.answer(text = 'это команда /start')

@dp.message(F.text.lower().startwith('fn'), NumInMsg())
async def nums_in_msg(message: Message, numbers: list[int]):
    await message.answer(text=f'i find: {", ".join(str(num) for num in numbers)}\n')

@dp.message(F.text.lower().startwith('fn'))
async def not_nums_in_msg(message: Message):
    await message.answer(text='not found :(')


if __name__ == '__main__':
    dp.run_polling(bot)