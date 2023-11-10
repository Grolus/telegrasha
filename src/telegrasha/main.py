
import config
import logging
import asyncio
import sys
import time

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from dispatcher import dispatcher as dp
from utils.constants import IS_ON_SERVER
from handler import *
# log
logging.basicConfig(level=logging.INFO)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token=config.TOKEN, session=session if IS_ON_SERVER else None)
    # And the run events dispatching
    await bot.send_message(1122505805, f'Я запустился ({time.ctime()})')
    await dp.start_polling(bot)

# run long-polling
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())