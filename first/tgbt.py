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

async def message_echo(message: Message):
    await message.answer(text = message.text)

async def photo_echo(message: Message):
    print(message)
    await message.reply_video(message.photo[0].file_id)
async def video_echo(message: Message):
    print(message)
    await message.reply_video(message.video.file_id)

async def sticker_echo(message: Message):
    print(message)
    await message.reply_sticker(message.sticker.file_id)

async def audio_echo(message: Message):
    print(message)
    await message.reply_audio(message.audio.file_id)

async def voice_echo(message: Message):
    print(message)
    await message.reply_video(message.voice.file_id)

async def video_note_echo(message: Message):
    print(message)
    await message.reply_video(message.video_note.file_id)

dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(help_message, Command(commands='help'))
dp.message.register(photo_echo, F.photo)
dp.message.register(video_echo, F.video)
dp.message.register(sticker_echo, F.sticker)
dp.message.register(audio_echo, F.audio)
dp.message.register(voice_echo, F.voice)
dp.message.register(video_note_echo, F.video_note)
dp.message.register(message_echo)


if __name__ == '__main__':
    dp.run_polling(bot)