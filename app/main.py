import asyncio
from .bot import bot, dp
from .main_handler import router as main_router


# Основная функция
async def main():
    # asyncio.create_task(check_commits())
    dp.include_router(main_router)
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
