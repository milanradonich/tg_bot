import logging

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '5468403221:AAGGdk30ishpYwenO3yBTylqGhKpiuP5LY8'

# # Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand('start', 'welcome descr'),
        types.BotCommand('hello-world', 'welcome descr'),
        # types.BotCommand('help', ' list of commands'),
    ])


@dp.message_handler(commands=['start', 'hello-world'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.full_name
    await message.reply(f"Привет, {user_name}!\nДобро пожаловать в бот-путешественник.\n"
                        f"Я помогу тебе найти жилье в разных странах и городах.")


@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    user_name = message.from_user.full_name
    if message.text.lower() == "привет":
        await message.reply(f'Привет, {user_name} ! Что будем искать?')
    else:
        await message.reply('Я вас не понял. Введите текст твердо и четко')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
