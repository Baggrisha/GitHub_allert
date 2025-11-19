import asyncio
import datetime
from zoneinfo import ZoneInfo

import aiohttp
import certifi
import ssl
import html

from .bot import bot
from .config import load_settings

# SSL контекст для GitHub
ssl_context = ssl.create_default_context(cafile=certifi.where())

def split_html(text: str, limit: int = 4096) -> list[str]:
    """
    Разбивает HTML текст на части не более limit символов,
    стараясь не резать теги и разрывать блоки по абзацам.
    """
    parts = []
    while len(text) > limit:
        # ищем последний перенос строки перед лимитом
        cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:]
    if text:
        parts.append(text)
    return parts


async def send_long_message(chat_id: int, text: str):
    """Отправка длинного сообщения частями в HTML parse mode"""
    for chunk in split_html(text):
        await bot.send_message(
            chat_id,
            chunk,
            parse_mode="HTML",
            disable_web_page_preview=True
        )


async def get_commits(repo: str, count: int = 1):
    """Получение последних коммитов из GitHub"""
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {
        "Authorization": f"token {load_settings().github_access_token}",
        "Accept": "application/vnd.github+json"
    }
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
    ) as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 401:
                raise PermissionError("Unauthorized — неверный токен или нет доступа")
            resp.raise_for_status()
            data = await resp.json()
            return data[:count]


def format_commit_message(commit: dict) -> str:
    """Форматирует коммит в HTML с безопасным экранированием"""
    author = html.escape(commit["commit"]["committer"]["name"])
    message = commit["commit"]["message"]
    commit_date_iso = commit["commit"]["committer"]["date"]
    commit_link = commit["html_url"]
    sha = html.escape(commit["sha"][:7])

    dt = datetime.datetime.fromisoformat(commit_date_iso)
    dt_tmz = dt.astimezone(ZoneInfo(load_settings().tz))
    commit_date = dt_tmz.strftime("%H:%M:%S %d.%m.%Y")

    # Разбиваем текст коммита на заголовок и тело
    if "\n\n" in message:
        title, body = message.split("\n\n", 1)
        main_text = f"✅ Обновление загружено:\n<b>{html.escape(title)}</b>\n\n📝 Комментарий:\n<pre>{html.escape(body)}</pre>"
    else:
        main_text = f"✅ Обновление загружено:\n<b>{html.escape(message)}</b>"

    footer = (
        f"👤 Автор: <b>{author}</b>\n"
        f"🕒 Дата коммита: <code>{commit_date}</code>\n"
        f"🧬 SHA: <code>{sha}</code>\n"
        f"🔗 Ссылка: <a href=\"{commit_link}\">Открыть на GitHub</a>"
    )

    return f"{main_text}\n\n{footer}"


async def check_commits():
    """Фоновая проверка новых коммитов каждые 60 секунд"""
    last_seen = {}
    while True:
        for repo in load_settings().github_repos:
            try:
                commits = await get_commits(repo)
                commit = commits[0]
                sha = commit["sha"]
                if last_seen.get(repo) != sha:
                    last_seen[repo] = sha
                    text = format_commit_message(commit)
                    for admin_id in load_settings().admin_user_id:
                        await send_long_message(admin_id, text)
            except Exception as e:
                print(f"Ошибка при проверке коммитов {repo}: {e}")
        await asyncio.sleep(60)

