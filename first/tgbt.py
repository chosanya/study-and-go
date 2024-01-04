from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

bot_token = '6742804978:AAESNA7-XrAn6dXK64tzGE3tt5EtJzxkzRY'
bot = Bot(token = bot_token)
dp = Dispatcher()

@dp.message(Command(commands = 'start'))
async def process_start_command(message: Message):
    await message.answer('Привет! я бот-попугай')
@dp.message(Command(commands = 'help'))
async def help_message(message: Message):
    await message.answer(
        'напиши мне что-то'
        'а я за тобой повторю. аххаа как оригинально'
    )

@dp.message()
async def messg(message: Message):
    await message.answer(text = message.text)

if __name__ == '__main__':
    dp.run_polling(bot)