from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command,CommandStart
from aiogram.types import Message
import random

bot_token = '6742804978:AAESNA7-XrAn6dXK64tzGE3tt5EtJzxkzRY'
bot = Bot(token = bot_token)
dp = Dispatcher()
att = 5
users = {}

def rand_num() -> int:
    return random.randint(1,100)

async def process_start_command(message: Message):
    await message.answer('Привет!\nДавайте сыграем в игру "Угадай число"?\n\n'
        'Чтобы получить правила игры и список доступных '
        'команд - отправьте команду /help')
    if message.from_user.id not in users:
        users[message.from_user.id] = {
             'in_game': False,
             'number': 0,
             'attempts': None,
             'total_games': 0,
             'wins': 0}

async def help_message(message: Message):
    await message.answer( f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
        f'а вам нужно его угадать\nУ вас есть {att} '
        f'попыток\n\nДоступные команды:\n/help - правила '
        f'игры и список команд\n/cancel - выйти из игры\n'
        f'/stat - посмотреть статистику\n\nДавай сыграем?'
    )

async def process_stat_command(message: Message):
    await message.answer(
        f'Всего игр сыграно: {users[message.from_user.id]["total_games"]}\n'
        f'Игр выиграно: {users[message.from_user.id]["wins"]}'
    )

async def cancel_command(messagge: Message):
    if users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = False
        await messagge.answer('Вы вышли из игры, если захотите'
                              'сыграть еще раз, то напишите об этом')

    else:
        await messagge.answer('Мы и так не играем, бро')

@dp.message(F.text.lower().in_(['да', 'давай', 'сыграем', 'игра',
                                'играть', 'хочу играть', 'ок']))
async def positive_ans(message: Message):
    if not users[message.from_user.id]['in_game']:
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['number'] = rand_num()
        users[message.from_user.id]['attempts'] = att
        await message.answer('ура! я загадал число от 1 до 100 (не вкулючительно)'
                             'попробуй угадать!!!!!')

    else:
        await message.answer('пока мы не играем в игру я не могу загадать число(((')

@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def negative_ans(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer('ну и ладно(')
    else:
        await message.answer('так мы же уже играем.'
                             'кидай числа от 1 до 100'
                             ' и не выпендривайся')

@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <=100)
async def num_numans(message: Message):
    if users.get(message.from_user.id,{}).get('in_game'):
        if int(message.text) == users[message.from_user.id]['number']:
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games']+=1
            users[message.from_user.id]['wins']+=1
            users[message.from_user.id]['attempts'] = 0
            await message.answer('вы угадали!!'
                                 'сыграем еще разок?')
        elif users[message.from_user.id]['attempts']==0:
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games']+=1
            await message.answer('вы проиграли :(( у вас больше не осталось попыток'
                                 'мое число ' + str({users[message.from_user.id]['number']}) +
                                 ' сыграем еще раз?')
        elif int(message.text) > users[message.from_user.id]['number']:
            users[message.from_user.id]['attempts']-=1
            await message.answer('мое число меньше!! попробуй еще раз!!')
        elif int(message.text) < users[message.from_user.id]['number']:
            users[message.from_user.id]['attempts']-=1
            await message.answer('мое число больше!! попробуй еще раз!!')

    else:
        await message.answer('мы еще не играем.. хотите начать?')

async def other_message(message: Message):
    if users.get(message.from_user.id,{}).get('in_game'):
        await message.answer('мы же сейчас играем.. кидайте число от 1 до 100')
    else:
        await message.answer('я довольно ограниченный бот, давайте сыграем в игру((')

dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_stat_command, Command(commands='stats'))
dp.message.register(help_message, Command(commands='help'))
dp.message.register(cancel_command, Command(commands='cancel'))
dp.message.register(other_message)


if __name__ == '__main__':
    dp.run_polling(bot)