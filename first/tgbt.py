import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)
bot_token = '6742804978:AAESNA7-XrAn6dXK64tzGE3tt5EtJzxkzRY'
bot = Bot(token = bot_token)
dp = Dispatcher()

#class Ans_Check(BaseFilter):
#    async def __call__(self, message: Message) -> bool:
#        for word in message:
#            norm_ans = word.replace(',','').replace(',','').stprip()
#        return norm_ans == ans

@dp.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer('Привет! Я - бот, который поможет тебе нарешать '
                        'тестовую часть ЕГЭ по русскому языку. '
                         'Напиши мне /help, чтобы узнать, что я могу.')
@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Ты можешь как решать конкретные задания, так '
                         'и решить целый вариант тестовой части, '
                         'составленный из заданий с РЕШУЕГЭ и банка ФИПИ. '
                         'Чтобы перейти к заданиям - напиши /menu ')

@dp.message(Command('menu'))
async def cmd_menu(message: Message):
    await message



dp.message.register(cmd_menu, Command('menu'))
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())