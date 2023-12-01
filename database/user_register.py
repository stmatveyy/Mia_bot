from database import database_func

async def check_user_data(num: int, message) -> None | bool:
    number_exists = await database_func.postgres_do_view(f'SELECT * FROM "public.users" WHERE number = {int(str(num)[0:])}')
    if number_exists != []:
        await database_func.postgres_do_change(f'UPDATE public."public.users" SET telegram_id = {message.from_user.id} WHERE number = {int(str(num)[0:])}')
        return True
    else:
        return False

async def check_if_registered(id_:int) -> bool:
    id_exists = await database_func.postgres_do_view(f'SELECT * FROM "public.users" WHERE telegram_id = {id_}')
    return False if id_exists == [] else True