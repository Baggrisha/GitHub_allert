import logging
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Update
from typing import Any, Callable, Awaitable, Dict

from .config import Settings
from .db import Database

logger = logging.getLogger(__name__)


class InjectDependenciesMiddleware(BaseMiddleware):
    """Middleware для внедрения зависимостей в обработчики"""
    
    def __init__(self, settings: Settings, db: Database):
        self._settings = settings
        self._db = db

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        # Кладём зависимости в data, чтобы их можно было получать в сигнатурах хендлеров
        data.setdefault("settings", self._settings)
        data.setdefault("db", self._db)
        return await handler(event, data)
