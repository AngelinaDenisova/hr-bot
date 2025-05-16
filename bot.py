import asyncio

from aiogram import Dispatcher

import utils
from bot_routers.answers import router as answers_router
from bot_routers.callbacks import router as callback_router
from bot_routers.introduction import router as introduction_router
from bot_routers.unknown import router as unknown_router

dp = Dispatcher()




async def main() -> None:
    bot = utils.get_bot()

    asyncio.create_task(utils.auto_checker())

    # And the run events dispatching
    dp.include_router(introduction_router)
    dp.include_router(callback_router)
    dp.include_router(answers_router)
    dp.include_router(unknown_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
