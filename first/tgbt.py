from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType

bot_token = '6742804978:AAESNA7-XrAn6dXK64tzGE3tt5EtJzxkzRY'
bot = Bot(token = bot_token)
dp = Dispatcher()


async def process_start_command(message: Message):
    await message.answer('Привет! я бот-попугай')

async def help_message(message: Message):
    await message.answer(
        'напиши мне что-то'
        'а я за тобой повторю. аххаа как оригинально'
    )

@dp.message()
async def send_echo(message: Message):
    try:
        print(message.model_dump_json(indent=4, exclude_none=True))
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        message.answer(text='ха-ха соси хуй')

dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(help_message, Command(commands='help'))



if __name__ == '__main__':
    dp.run_polling(bot)