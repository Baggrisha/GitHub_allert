"""Простой шаблон конфигурации на pydantic.

Заменяйте/расширяйте поля по необходимости.
"""
import os

from pydantic import BaseModel


class Settings(BaseModel):
    bot_token: str = ""
    github_access_token: str = ""
    admin_user_id: list[int] = 0
    github_repos: list[str] = ""
    commit_count: int = 5
    tz: str = "Europe/Moscow"


def load_settings() -> Settings:
    admin_user_str = os.getenv("ADMIN_USER_ID", "0")  # строка, например "123,456"
    github_repos_str = os.getenv("GITHUB_REPOS", "0")  # строка, например "["ff/gg", "gg/ff"]"
    admin_user_list = [int(x) for x in admin_user_str.split(",") if x]
    github_repos_list = [str(x) for x in github_repos_str.split(",") if x]
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        github_access_token=os.getenv("GITHUB_ACCESS_TOKEN", ""),
        github_repos=github_repos_list,
        commit_count=int(os.getenv("COMMIT_COUNT", "5")),
        admin_user_id=admin_user_list,
        tz=os.getenv("TZ", "Europe/Moscow"),
    )
