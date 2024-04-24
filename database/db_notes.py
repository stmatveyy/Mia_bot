from database.database_func import Database

# Интерфейс для удаления заметок / напоминаний / ... из своих таблиц. Передавать тип сущности при вызове.

allowed_types:list[str] = ['notes', 'reminders']

async def check_user_id(telegram_id: int, database: Database) -> int:
    '''Возвращает ID пользователя из таблицы.'''
    res = await database.view(query=f'SELECT "id" FROM "public.users" WHERE "telegram_id"={telegram_id}')
    return int(res[0][0])


async def check_entity_id(telegram_id: int, database: Database, type_: str) -> list[int]:
    '''Возвращает список ID сущностей из таблицы.'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    user_id = await check_user_id(telegram_id, database)
    final_list = []
    raw_data = await database.view(f'SELECT "id" FROM "public.{type_}" WHERE "fk_user_{type_[:-1]}"={user_id}')
    for el in raw_data:
        final_list.append(el[0])
    return final_list


async def write_entity(text: str,
                     telegram_id: int,
                     database: Database,
                     type_:str) -> None:
    '''Записывает сущность в таблицу.'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    short_type = type_[:-1]
    user_id = await check_user_id(telegram_id, database)
    await database.change(f'INSERT INTO "public.{type}"({short_type}_text, fk_user_{short_type}) VALUES ({text}, {user_id})')


async def view_all_entities(telegram_id: int, database: Database, type_:str) -> str | int:
    '''Возвращает текст всех сущностей из таблицы'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    user_id = await check_user_id(telegram_id, database)
    short_type:str = type_[:-1]
    final_str = ''
    counter = 1
    raw_data = await database.view(f'SELECT "{short_type}_text" FROM "public.{type}" WHERE "fk_user_{type}"={user_id}')
    if raw_data == []:
        return 0
    else:
        for el in raw_data:
            final_str += (str(counter) + ': <i>' + el[0].strip() + '</i>\n')
            counter += 1
        return final_str, counter


async def delete_entity(telegram_id: int,
                      index: int,
                      database: Database,
                      type_:str) -> None | int:
    '''Удаляет выбранную сущность пользователя.'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    user_id = await check_user_id(telegram_id, database)
    entities_list = await check_entity_id(telegram_id, database, type_='notes')
    await database.change(f'DELETE FROM "public.{type_}" WHERE "fk_user_{type[:-1]}"={user_id} AND id = {entities_list[index-1]}')


async def delete_all_entities(telegram_id: int, database: Database, type_:str) -> None:
    '''Удаляет все сущности пользователя.'''
    user_id = await check_user_id(telegram_id, database)
    await database.change(f'DELETE FROM "public.{type_}" WHERE "fk_user_{type_[:-1]}"={user_id}')
# Передавать "'текст'" в write_entity
