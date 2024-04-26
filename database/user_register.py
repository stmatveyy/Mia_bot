from database.database_func import Database
from misc.SQL_dict import SQL_queries as sql

async def check_user_data(num: int, message, database: Database) -> None | bool:
    '''Возвращает наличие номера телефона в базе данных,
    регистрирует пользователя если телефон найден.'''
    number_exists = await database.view(sql.CHECK_NUM(num))

    if number_exists != []:
        await register_user(message= message, num= num, database= database)
        return True
    
    else:
        return False


async def register_user(message, num: int, database: Database) -> None:
    await database.change(sql.REG_USER(message, num))


async def check_if_registered(id_: int, database: Database) -> bool:
    '''Возвращает наличие telegram_id в базе данных'''
    id_exists = await database.view(f'SELECT * FROM "public.users" WHERE telegram_id = {id_}')
    return False if id_exists == [] else True