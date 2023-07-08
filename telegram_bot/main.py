import logging
import os

from aiogram import Dispatcher
from aiogram.utils.executor import start_polling, start_webhook
from loguru import logger

# from tg_bot.filters.admin import IsAdminFilter
from tg_bot.middlewares.throttling import ThrottlingMiddleware
# from tg_bot.services.admins_notify import on_startup_notify
from tg_bot.services.setting_commands import set_default_commands
from loader import dp


# def register_all_middlewares(dispatcher: Dispatcher) -> None:
#     logger.info('Registering middlewares')
#     dispatcher.setup_middleware(ThrottlingMiddleware())
#
#
# def register_all_filters(dispatcher: Dispatcher) -> None:
#     logger.info('Registering filters')
#     dispatcher.filters_factory.bind(IsAdminFilter)


def register_all_handlers(dispatcher: Dispatcher) -> None:
    from tg_bot import handlers
    logger.info('Registering handlers')


async def register_all_commands(dispatcher: Dispatcher) -> None:
    logger.info('Registering commands')
    await set_default_commands(dispatcher.bot)


async def on_startup(dispatcher: Dispatcher, webhook_url: str = None) -> None:
    # register_all_middlewares(dispatcher)
    # register_all_filters(dispatcher)
    register_all_handlers(dispatcher)
    await register_all_commands(dispatcher)
    # # Get current webhook status
    # webhook = await dispatcher.bot.get_webhook_info()
    #
    # if webhook_url:
    #     await dispatcher.bot.set_webhook(webhook_url)
    #     logger.info('Webhook was set')
    # elif webhook.url:
    #     await dispatcher.bot.delete_webhook()
    #     logger.info('Webhook was deleted')

    # await on_startup_notify(dispatcher)

    logger.info('Bot started')


async def on_shutdown(dispatcher: Dispatcher) -> None:
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    logger.info('Bot shutdown')


if __name__ == "__main__":
    logger.add(
        "tgbot.log",
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        rotation="10 KB",
        compression="zip",
    )
    logger.info("Initializing bot")

    # # Webhook settings
    # HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
    # WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
    # WEBHOOK_PATH = f'/webhook/{config.tg_bot.token}'
    # WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
    # # Webserver settings
    # WEBAPP_HOST = '0.0.0.0'
    # WEBAPP_PORT = int(os.getenv('PORT', 5000))

    start_polling(
        dispatcher=dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
    )










# *********************************************
# import asyncio
# import logging
#
# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.types import Message
# from config import API_TOKEN
#
#
# logging.basicConfig(level=logging.INFO)
#
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)
#
#
# async def set_default_commands(dp):
#     await dp.bot.set_my_commands([
#         types.BotCommand('start', 'welcome descr'),
#         types.BotCommand('hello-world', 'welcome descr'),
#         # types.BotCommand('help', ' list of commands'),
#     ])
#
#
# @dp.message_handler(commands=['start', 'hello-world'])
# async def send_welcome(message: types.Message):
#     user_name = message.from_user.full_name
#     await message.reply(f"Привет, {user_name}!\nДобро пожаловать в бот-путешественник.\n"
#                         f"Я помогу тебе найти жилье в разных странах и городах.")
#
#
# @dp.message_handler(content_types=['text'])
# async def text_handler(message: types.Message):
#     user_name = message.from_user.full_name
#     if message.text.lower() == "привет":
#         await message.reply(f'Привет, {user_name} ! Что будем искать?')
#     else:
#         await message.reply('Я вас не понял. Введите текст твердо и четко')
#
#
# async def main():
#     await dp.start_polling(bot)
#
# if __name__ == '__main__':
#     asyncio.run(main())
