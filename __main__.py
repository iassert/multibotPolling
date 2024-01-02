import logging

from aiogram            import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot_   import Bot_
from config import Config

logging.basicConfig(level = logging.INFO)


class FormMain(StatesGroup):
	add_bot = State()

class Main:
    bot = Bot_()
    bot.init(Config.API_TOKEN)

    async def start(message: types.Message, state: FSMContext):
        await message.answer("Привет")

    async def send_add_bot(message: types.Message, state: FSMContext):
        await message.answer("Введите token: ")
        await FormMain.add_bot.set()

    async def add_bot(message: types.Message, state: FSMContext = None):
        await state.finish()

        from_user_id: int = message.from_user.id

        Main.bot = Bot_()
        Main.bot.init(message.text)
        successfully = Main.bot.start_polling(
            on_startup_  = Bot_.on_startup(from_user_id),
            on_shutdown_ = Bot_.on_shutdown(from_user_id)
        )
        if successfully:
            return await message.answer("Бот запущен")
        await message.answer("Не удалось запустить бота")


    def main():
        Main.bot.start_polling(
            on_startup_  = Bot_.on_startup(Config.CREATOR_ID),
            on_shutdown_ = Bot_.on_shutdown(Config.CREATOR_ID)
        )


Main.bot.dp.register_message_handler(
    Main.start,
    commands = "start",
    state = "*"
)
Main.bot.dp.register_message_handler(
    Main.send_add_bot,
    commands = "add_bot",
    state = "*"
)
Main.bot.dp.register_message_handler(
    Main.add_bot,
    content_types = types.ContentType.TEXT,
    state = FormMain.add_bot
)



if __name__ == "__main__":
    Main.main()
