"""Простой асинхронный фасад над sqlite (aiosqlite)."""
import asyncio
from typing import Any, Sequence

import aiosqlite


# Все SQL запросы держим здесь для простоты сопровождения
def INIT_SQL():
    INIT_SQL = """
    PRAGMA journal_mode=WAL;

    CREATE TABLE IF NOT EXISTS repos (
        repo TEXT PRIMARY KEY
    );
    """
    return INIT_SQL


class Database:
    """Асинхронный фасад над aiosqlite для МедиаШколы."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._lock = asyncio.Lock()

    async def init(self) -> None:
        """Инициализация БД с созданием таблиц и применением миграций"""
        import logging
        logger = logging.getLogger(__name__)

        async with aiosqlite.connect(self._db_path) as db:

            # Миграции
            migrations = [("""
        CREATE TABLE IF NOT EXISTS repos (
        repo TEXT PRIMARY KEY);""", "create_db")
            ]

            for migration_sql, column_name in migrations:
                try:
                    await db.execute(migration_sql)
                    await db.commit()
                    logger.info(f"✅ Миграция применена: добавлено поле {column_name}")
                except Exception as e:
                    if 'duplicate column' in str(e).lower():
                        logger.debug(f"Поле {column_name} уже существует, пропускаем миграцию")
                    else:
                        logger.warning(f"Ошибка при миграции {column_name}: {e}")

    # --- базовые методы ---
    async def execute(self, sql: str, params: Sequence[Any] | None = None):
        """Выполнение SQL-запроса без возврата результата."""
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(sql, params or [])
                await db.commit()

    async def fetchone(self, sql: str, params: Sequence[Any] | None = None):
        """Выполнение SQL-запроса и возврат первой строки результата (sqlite3.Row)."""
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, params or []) as cursor:
                return await cursor.fetchone()

    async def fetchall(self, sql: str, params: Sequence[Any] | None = None):
        """Выполнение SQL-запроса и возврат всех строк результата (список sqlite3.Row)."""
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, params or []) as cursor:
                return await cursor.fetchall()

    async def reset_all(self) -> None:
        """Очистка всех таблиц базы данных (удаление всех данных)."""
        async with self._lock:
            async with aiosqlite.connect(self._db_path) as db:
                tables = ["users", "curators", "codewords", "homework", "inspectors"]
                for table in tables:
                    await db.execute(f"DROP TABLE {table}")
                await db.commit()

    async def add_repo(self, repo: str| None = None):
        """Добавление нового репозитория или игнорирование, если уже существует."""
        await self.execute(
            "INSERT OR REPLACE INTO repos(repo) VALUES(?);",
            (repo,)
        )

    async def remove_repo(self, repo: str):
        """Удаляет репозиторий из таблицы."""
        await self.execute(
            "DELETE FROM repos WHERE repo = ?;",
            (repo,)
        )

    async def get_repos(self):
        """Возвращает список всех репозиториев."""
        rows = await self.fetchall("SELECT repo FROM repos;")
        return [row["repo"] for row in rows]