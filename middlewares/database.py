from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.database_func import Database
import keyboards.reply
from redis import Redis
from database.redis_func import RedisPool
import logging

class CommonMiddleWare(BaseMiddleware):
    '''Мидлварь для передачи экземпляров БД в хэндлеры'''
    def __init__(self, database: Database) -> None:
        assert database is not None, "Database is None when CommonMiddleWare is initialized"
        self.database = database
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        redis_pool = RedisPool()
        await redis_pool.__ainit__() 
        self.redis = redis_pool.client
        # Собираем словарь только тех пар, которые относятся к пользователю
        params_needed: list[str] = ["approved"]
    
        # Получаем параметр допуска пользователя к боту из Redis'a
        dependencies_redis_data: list = await self.redis.hmget(str(event.from_user.id), ["approved"])
        approved = dependencies_redis_data[0]
        
        logging.debug(f"Redis approved: {approved}. All dependencies: {dependencies_redis_data}")
        # Если значения такого ключa нет, пишем в бд статус конкретного пользователя
        # Эта часть отрабатывает только при первом запуске
        if approved is None:
            data["approved"] = 0
            user_specific_data: dict = {k:v for k, v in data.items() if k in params_needed} 
            await self.redis.hmset(str(event.from_user.id), user_specific_data)

        # Если статус пользователя - без доступа или он не отправил номер телефона, отшиваем его
        elif str(approved[0]) == "'0'" and event.text is not None:

            await event.answer(text="<b>Не получится воспользоваться ботом. </b>",
                               reply_markup=keyboards.reply.num_keyboard)
            return None
        
        data["database"] = self.database
        data["redis"] = self.redis

        result = await handler(event, data)

        # Если в хэндлере меняем значения data, то берем их тут
        if isinstance(result, tuple):
            # Проверка на вложенный кортеж, чтобы отправлять 2 значения сразу
            if isinstance(result[0], tuple):
                data[result[0][0]] = result[0][1]
                data[result[1][0]] = result[1][1]
                try:
                    data[result[2][0]] = result[2][1]
                except IndexError:
                    pass

                user_specific_data = {k:v for k, v in data.items() if k in params_needed}

            else:
                data[result[0]] = result[1]
                user_specific_data = {k:v for k, v in data.items() if k in params_needed}
            await self.redis.hmset(str(event.from_user.id), user_specific_data)

        return result
