import sys
import asyncio

from aiogram.bot.api    import log as aiolog
from aiogram.dispatcher import Dispatcher

from typing import Optional, List, Callable


def start_polling(
    dispatcher: Dispatcher, 
    *, 
    skip_updates:  bool = False, 
    reset_webhook: bool = True,
    on_startup:  Callable = None, 
    on_shutdown: Callable = None, 
    timeout: int = 20, 
    relax: float = 0.1, 
    fast:   bool = True,
    allowed_updates: Optional[List[str]] = None,
    wait: bool = False
):
    executor = Executor_(dispatcher, 
        skip_updates = skip_updates, 
        on_startup   = on_startup, 
        on_shutdown  = on_shutdown
    )
    
    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        asyncio.create_task(executor.astart_polling(
            reset_webhook = reset_webhook,
            timeout = timeout,
            relax   = relax,
            fast    = fast,
            allowed_updates = allowed_updates
        ))
        if wait:
            asyncio.wait()
    else:
        executor.start_polling(
            reset_webhook = reset_webhook,
            timeout = timeout,
            relax   = relax,
            fast    = fast,
            allowed_updates = allowed_updates
        )


class Executor_:
    def __init__(self, 
        dp: Dispatcher, 
        *,
        skip_updates:  bool = False,
        on_startup:  Callable = None,
        on_shutdown: Callable = None
    ):
        self.__dp: Dispatcher = dp
        self.__skip_updates:  bool   = skip_updates
        self.__on_startup:  Callable = on_startup
        self.__on_shutdown: Callable = on_shutdown


    def start_polling(self, 
        reset_webhook = None, 
        timeout: int = 20, 
        relax: float = 0.1, 
        fast = True,
        allowed_updates: Optional[List[str]] = None
    ):
        if sys.version_info < (3, 10):
            loop = asyncio.get_event_loop()
        else:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()

            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._startup_polling())
            loop.create_task(
                self.__dp.start_polling(
                    reset_webhook = reset_webhook, 
                    timeout = timeout,
                    relax = relax, 
                    fast = fast, 
                    allowed_updates = allowed_updates
                )
            )
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            # loop.stop()
            pass
        except BaseException as ex:
            aiolog.error(f"{ex.__class__.__name__}: {ex}")
        finally:
            loop.run_until_complete(self._shutdown_polling())
            aiolog.warning("Goodbye!")

    async def astart_polling(self, 
        reset_webhook = None, 
        timeout: int = 20, 
        relax: float = 0.1, 
        fast = True,
        allowed_updates: Optional[List[str]] = None
    ):
        try:
            await self._startup_polling()
            await self.__dp.start_polling(
                reset_webhook = reset_webhook, 
                timeout = timeout,
                relax = relax, 
                fast = fast, 
                allowed_updates = allowed_updates
            )
        except (KeyboardInterrupt, SystemExit):
            # loop.stop()
            pass
        finally:
            await self._shutdown_polling()
            aiolog.warning("Goodbye!")   

    async def _startup_polling(self):
        await self._welcome()

        if self.__skip_updates:
            await self.__dp.reset_webhook(True)
            await self.__dp.skip_updates()
            aiolog.warning(f'Updates were skipped successfully.')
        
        if self.__on_startup is not None:
            await self.__on_startup(self.__dp)

    async def _shutdown_polling(self, wait_closed = False):
        if self.__on_shutdown is not None:
            await self.__on_shutdown(self.__dp)

        await self._shutdown()

        if wait_closed:
            await self.__dp.wait_closed()

    async def _shutdown(self):
        self.__dp.stop_polling()
        
        await self.__dp.storage.close()
        await self.__dp.storage.wait_closed()
        
        session = await self.__dp.bot.get_session()
        await session.close()

    async def _welcome(self):
        user = await self.__dp.bot.me
        aiolog.info(f"Bot: {user.full_name} [@{user.username}]")
