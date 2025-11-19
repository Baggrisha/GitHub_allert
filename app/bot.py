from aiogram import Bot, Dispatcher

from .config import load_settings

bot = Bot(token=load_settings().bot_token)
dp = Dispatcher()
