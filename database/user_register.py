from database.database_func import Database


async def check_user_data(num: int, message, database: Database) -> None | bool:
    '''Возвращает наличие номера телефона в базе данных,
    регистрирует пользователя если телефон найден.'''
    number_exists = await database.view(f'SELECT * FROM "public.users" WHERE number = {int(str(num)[0:])}')
    if number_exists != []:
        await database.change(f'UPDATE public."public.users" SET telegram_id = {message.from_user.id} WHERE number = {int(str(num)[0:])}')
        return True
    else:
        return False


async def check_if_registered(id_: int, database: Database) -> bool:
    '''Возвращает наличие telegram_id в базе данных'''
    id_exists = await database.view(f'SELECT * FROM "public.users" WHERE telegram_id = {id_}')
    return False if id_exists == [] else True