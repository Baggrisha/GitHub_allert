# Команды бота
import html

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .config import load_settings
from .scripts import get_commits, send_long_message, format_commit_message

router = Router()

@router.message(Command("last_commit"))
async def last_commits(message: Message):
    if len(message.text.split()) < 2:
        return await message.answer("❌ Ты не указал репозиторий")
    repo = message.text.split("/last_commit ")[1]
    try:
        commits = await get_commits(repo, 10)
    except Exception as e:
        return await message.answer(f"Ошибка: {html.escape(str(e))}")

    # Заголовок для репозитория
    header = f"📌 Последние коммиты в <b>{html.escape(repo)}</b>:\n\n"
    text_parts = [header]

    for c in commits:
        text_parts.append(format_commit_message(c))
        text_parts.append("\n")  # разделитель между коммитами

    # Собираем текст
    text = "\n".join(text_parts)

    # Безопасная отправка длинного HTML
    await send_long_message(message.chat.id, text)

@router.message(Command("last_commits"))
async def last_commits(message: Message):
    repos = load_settings().github_repos

    for repo in repos:
        try:
            commits = await get_commits(repo, 10)
        except Exception as e:
            return await message.answer(f"Ошибка: {html.escape(str(e))}")

        # Заголовок для репозитория
        header = f"📌 Последние коммиты в <b>{html.escape(repo)}</b>:\n\n"
        text_parts = [header]

        for c in commits:
            text_parts.append(format_commit_message(c))
            text_parts.append("\n")  # разделитель между коммитами

        # Собираем текст
        text = "\n".join(text_parts)

        # Безопасная отправка длинного HTML
        await send_long_message(message.chat.id, text)
