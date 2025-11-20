# Команды бота
import html
import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .config import load_settings
from .db import Database
from .scripts import get_commits, send_long_message, format_commit_message

router = Router()

@router.message(Command("last_commit"))
async def last_commits(message: Message):
    if not message.from_user.id in load_settings().admin_user_id:
        return
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
async def last_commits(message: Message, db: Database):
    if message.from_user.id not in load_settings().admin_user_id:
        return

    repos = await db.get_repos()

    if not repos:
        return await message.answer("❌ В БД нет ни одного репозитория.")
    if len(message.text.split()) > 1:
        try:
            count = int(message.text.split()[1])
        except ValueError:
            await message.answer("Не правильное число коммитов\n\n/last_commits <counts>")
    else:
        count = load_settings().commit_count
    for repo in repos:
        try:
            commits = await get_commits(repo, count)
        except Exception as e:
            await message.answer(f"Ошибка для {html.escape(repo)}: {html.escape(str(e))}")
            continue

        header = f"📌 Последние коммиты в <b>{html.escape(repo)}</b>:\n\n"
        parts = [header]

        for c in commits:
            parts.append(format_commit_message(c))
            parts.append("\n")

        text = "\n".join(parts)

        await send_long_message(message.chat.id, text)


@router.message(Command("add_repo"))
async def cmd_add_repo(message: Message, db: Database):
    if message.from_user.id not in load_settings().admin_user_id:
        return

    parts = message.text.split(maxsplit=1)
    repo_input = parts[1].strip()

    # ----- если пользователь прислал URL -----
    if re.match(r"^https://github\.com/", repo_input):
        # Пример URL:
        # https://github.com/owner/repo
        m = re.match(r"^https://github\.com/([^/]+)/([^/]+)", repo_input)
        if not m:
            return await message.answer("❌ Не удалось распарсить URL GitHub.")

        owner = m.group(1)
        repo_name = m.group(2)
        repo = f"{owner}/{repo_name}"

    # ----- если прислал owner/repo -----
    else:
        if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", repo_input):
            return await message.answer("❌ Некорректный формат. Используйте <b>owner/repo</b> или URL GitHub.")
        repo = repo_input
    await db.add_repo(repo)

    await message.answer(f"✅ Репозиторий <b>{html.escape(repo)}</b> добавлен.")


@router.message(Command("remove_repo"))
async def cmd_remove_repo(message: Message, db: Database):
    if message.from_user.id not in load_settings().admin_user_id:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer(
            "⚠️ Использование: <b>/remove_repo &lt;repo&gt;</b>"
        )

    repo_input = parts[1].strip()

    # ---- Если передан URL ----
    if re.match(r"^https://github\.com/", repo_input):
        m = re.match(r"^https://github\.com/([^/]+)/([^/]+)", repo_input)
        if not m:
            return await message.answer("❌ Не удалось распарсить URL GitHub.")

        owner = m.group(1)
        repo_name = m.group(2)
        repo = f"{owner}/{repo_name}"

    # ---- Если передано owner/repo ----
    else:
        if not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", repo_input):
            return await message.answer(
                "❌ Некорректный формат. Используйте <b>owner/repo</b> или GitHub URL."
            )
        repo = repo_input

    # ---- Удаление из БД ----
    exist = await db.get_repos()
    if repo in exist:
        await db.remove_repo(repo)
        msg = f"🗑 Репозиторий <b>{html.escape(repo)}</b> удалён."
    else:
        msg = f"⚠️ Репозиторий <b>{html.escape(repo)}</b> не найден в базе."

    await message.answer(msg)


@router.message(Command("list_repos"))
async def cmd_list_repos(message: Message, db: Database):
    if message.from_user.id not in load_settings().admin_user_id:
        return

    repos = await db.get_repos()

    if not repos:
        return await message.answer("📭 Список репозиториев пуст.")

    text = "📦 <b>Список репозиториев:</b>\n\n"
    text += "\n".join(
        f"• <a href='https://github.com/{html.escape(r)}'>{html.escape(r)}</a>"
        for r in repos
    )
    await message.answer(text)
