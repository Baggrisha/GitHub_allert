"""Простой шаблон конфигурации на pydantic.

Заменяйте/расширяйте поля по необходимости.
"""
import os

from pydantic import BaseModel


class Settings(BaseModel):
    bot_token: str = ""
    github_access_token: str = ""
    admin_user_id: list[int] = 0
    commit_count: int = 5
    db_path: str = "/app/data/bot.db"
    tz: str = "Europe/Moscow"


def load_settings() -> Settings:
    admin_user_str = os.getenv("ADMIN_USER_ID", "0")  # строка, например "123,456"
    admin_user_list = [int(x) for x in admin_user_str.split(",") if x]
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        github_access_token=os.getenv("GITHUB_ACCESS_TOKEN", ""),
        commit_count=int(os.getenv("COMMIT_COUNT", "5")),
        admin_user_id=admin_user_list,
        db_path=os.getenv("DB_PATH", "/app/data/bot.db"),
        tz=os.getenv("TZ", "Europe/Moscow"),
    )
