import asyncio

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from app.config import load_settings
from app.db import Database
from app.middlewares import InjectDependenciesMiddleware
from app.scripts import check_commits
from .bot import bot, dp
from .main_handler import router as main_router


async def setup_bot_commands(bot: Bot) -> None:
    """Настройка команд бота для отображения в меню"""
    commands = [
        BotCommand(command="last_commit", description="📌 Посмотреть последний коммит конкретного репозитория"),
        BotCommand(command="last_commits", description="🔥 Последние коммиты всех твоих репозиториев"),
        BotCommand(command="add_repo", description="➕ Добавить новый репозиторий в список"),
        BotCommand(command="remove_repo", description="🗑 Удалить репозиторий из списка"),
        BotCommand(command="remove_all_repo", description="🗑 Удалить все репозитории из списка"),
        BotCommand(command="my_repos", description="📝 Список всех твоих репозиториев"),
    ]
    for admin in load_settings().admin_user_id:
        try:
            await bot.set_my_commands(
                commands,
                scope=BotCommandScopeChat(chat_id=admin)
            )
        except Exception:
            pass


# Основная функция
async def main():
    db = Database(load_settings().db_path)
    await db.init()
    asyncio.create_task(check_commits(db))

    dp.message.middleware(InjectDependenciesMiddleware(load_settings(), db))

    dp.include_router(main_router)
    await setup_bot_commands(bot)
    try:
        await dp.start_polling(bot, handle_signals=False)
    except Exception as e:
        print(f"Polling error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
    except Exception as e:
        print(f"Unexpected error: {e}")
