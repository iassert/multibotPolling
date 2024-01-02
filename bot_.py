import typing
import logging
import asyncio

import executor_

from aiogram            import Bot, types
from aiogram.types      import base
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions            import RetryAfter, BotBlocked
from aiogram.dispatcher.handler          import Handler
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from typing import Optional, List, Callable


class Bot_:
    def __init__(self, bot: Bot = None, dp: Dispatcher = None) -> None:
        self.bot: Bot = bot
        self.dp: Dispatcher = dp


    def init(self, token: str, message_handlers: Handler = None) -> bool:
        try:
            self.bot: Bot = Bot(token = token)#, server = Config.LOCAL_SERVER)
        except BaseException as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")
            return False

        self.dp: Dispatcher = Dispatcher(self.bot, storage = MemoryStorage())
        self.dp.middleware.setup(LoggingMiddleware())

        if message_handlers is not None:
            self.dp.message_handlers = message_handlers
        return True


    @staticmethod
    def on_startup(chat_id: int) -> Callable:
        async def _on_startup(dp: Dispatcher):
            bot_ = Bot_(dp.bot, dp)
            await bot_.send_message(chat_id, "Бот запущен")

        return _on_startup

    @staticmethod
    def on_shutdown(chat_id: int) -> Callable:
        async def _on_shutdown(dp: Dispatcher):
            logging.warning('Shutting down..')

            await dp.bot.send_message(chat_id, "Бот Выключен")

            logging.warning('Bye!')

        return _on_shutdown


    def start_polling(self,
        *, 
        skip_updates:  bool    = True, 
        reset_webhook: bool    = True,
        on_startup_:  Callable = None, 
        on_shutdown_: Callable = None, 
        timeout: int = 300, 
        relax: float = 0.1, 
        fast:   bool = True,
        allowed_updates: Optional[List[str]] = None,
        wait: bool = False
    ) -> bool:
        try:
            executor_.start_polling(
                dispatcher    = self.dp,
                skip_updates  = skip_updates, 
                reset_webhook = reset_webhook,
                on_startup    = on_startup_, 
                on_shutdown   = on_shutdown_, 
                timeout = timeout, 
                relax   = relax, 
                fast    = fast,
                allowed_updates = allowed_updates,
                wait = wait
            )
            return True
        except BaseException as ex:
            logging.error(f"{ex.__class__.__name__}: {ex}")
        return False
    

    async def send_message(self,
        chat_id:    typing.Union[base.Integer, base.String],
        text:       base.String,
        parse_mode: typing.Optional[base.String] = "html",
        entities:   typing.Optional[typing.List[types.MessageEntity]] = None,
        disable_web_page_preview:    typing.Optional[base.Boolean] = True,
        message_thread_id:           typing.Optional[base.Integer] = None,
        disable_notification:        typing.Optional[base.Boolean] = None,
        protect_content:             typing.Optional[base.Boolean] = None,
        reply_to_message_id:         typing.Optional[base.Integer] = None,
        allow_sending_without_reply: typing.Optional[base.Boolean] = None,
        reply_markup: typing.Union[
            types.InlineKeyboardMarkup,
            types.ReplyKeyboardMarkup,
            types.ReplyKeyboardRemove,
            types.ForceReply, 
            None
        ] = None,
    ) -> types.Message | None:
        async def _send_message():
            return await self.bot.send_message(
                chat_id,
                text,
                parse_mode,
                entities,
                disable_web_page_preview,
                message_thread_id,
                disable_notification,
                protect_content,
                reply_to_message_id,
                allow_sending_without_reply,
                reply_markup,
            )

        while True:
            try:
                return await _send_message()
            except RetryAfter as ex:
                await asyncio.sleep(ex.timeout)
                continue
            except BotBlocked:
                ...
            except BaseException as ex:
                logging.error(f"{ex.__class__.__name__}: {ex}")
            return
