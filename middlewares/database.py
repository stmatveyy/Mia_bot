from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.database_func import Database
import keyboards.reply
from redis import Redis

class CommonMiddleWare(BaseMiddleware):
    '''Мидлварь для передачи экземпляров БД в хэндлеры'''
    def __init__(self, database: Database, redis: Redis) -> None:
        assert database, "Database is None when CommonMiddleWare is initialized"
        assert redis, "Redis is None when CommonMiddleWare is initialized"

        self.database = database
        self.redis = redis

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Устанавливаем значения для локальной data
        data["approved"] = 0
        data["notifications"] = 0

        # Собираем словарь только тех пар, которые относятся к пользователю
        params_needed: list = ["approved", "notifications"]
        user_specific_data: dict = {k:v for k,v in data.items() if k in params_needed} 

        # Получаем параметр допуска пользователя к боту из Redis'a
        approved: list = await self.redis.hmget(str(event.from_user.id), ["approved"]) 

        # Если значения такого ключ нет, пишем в бд статус конкретного пользователя 
        # Эта часть отрабатывает только при первом запуске
        if approved[0] is None:
            self.redis.hmset(str(event.from_user.id), user_specific_data)

        # Если статус пользователя - без доступа или он не отправил номер телефона, отшиваем его 
        elif str(approved[0]) == "b'0'" and event.text != None:
            
            await event.answer(text="<b>Без номера телефона не получится воспользоваться ботом :(</b>",
                               reply_markup=keyboards.reply.num_keyboard)
            return None
        
        data["database"] = self.database
        data["redis"] = self.redis

        print("DB is passed to handler")
        result = await handler(event, data)

        if isinstance(result, tuple):
            data[result[0]] = result[1]
            await self.redis.hmset(str(event.from_user.id), user_specific_data)

        print(data["approved"])
        return result
