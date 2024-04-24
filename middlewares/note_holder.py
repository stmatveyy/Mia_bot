from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class CommonMiddleWare(BaseMiddleware):
    '''Мидлварь для передачи текста сообщения между хэндлерами'''

    def __init__(self) -> None:
        ...

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # Устанавливаем значения для локальной data
        
        data['curr_text'] = ""

        # Собираем словарь только тех пар, которые относятся к пользователю
        params_needed: list[str] = ["curr_text"]
        user_specific_data: dict = {k:v for k, v in data.items() if k in params_needed} 

        result = await handler(event, data)

        # Если в хэндлере меняем значения data, то берем их тут
        if isinstance(result, tuple):
            data[result[0]] = result[1]

        return result
