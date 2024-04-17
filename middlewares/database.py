from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.database_func import Database
import keyboards.reply


class CommonMiddleWare(BaseMiddleware):
    '''Мидлварь для передачи экземпляра БД в хэндлеры'''
    def __init__(self, database: Database) -> None:
        assert database, "Database is None when PrepMiddleware is initialized"
        self.database = database

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        try:

            approved: bool = data.get('approved')
            if approved is None:
                data['approved'] = None
            print('before check: ', approved)

            if approved is False:
                await event.message.reply("<b>Без номера телефона не получится воспользоваться ботом :(</b>", reply_markup=keyboards.reply.num_keyboard2)
                return

        except KeyError:
            data['approved'] = None

        data['database'] = self.database
        data['notifications'] = False

        print("DB is passed to handler")
        result = await handler(event, data)

        if isinstance(result, tuple):
            data[result[0]] = result[1]

        print(data['approved'])
        return result
