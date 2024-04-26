from database.database_func import Database
from misc.SQL_dict import SQL_queries as sql

# Интерфейс для удаления заметок / напоминаний / ... из своих таблиц. Передавать тип сущности при вызове.

allowed_types:list[str] = ['notes', 'reminders']

async def check_user_id(telegram_id: int, database: Database) -> int:
    '''Возвращает ID пользователя из таблицы.'''
    res = await database.view(query=sql.USER_ID(telegram_id))
    return int(res[0][0])


async def check_entity_id(telegram_id: int, database: Database, type_: str) -> list[int]:
    '''Возвращает список ID сущностей из таблицы.'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    user_id = await check_user_id(telegram_id, database)
    final_list = []
    raw_data = await database.view(sql.ENTITY_ID(type_, telegram_id))
    for el in raw_data:
        final_list.append(el[0])
    return final_list


async def write_entity(text: str,
                       telegram_id: int,
                       database: Database,
                       type_: str,
                       timestamp=0) -> None:
    
    '''Записывает сущность в таблицу.'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    short_type = type_[:-1]
    user_id = await check_user_id(telegram_id, database)
    
    match type_:

        case 'reminders':
            assert timestamp !=0, "Timestamp is not defined"
            await database.change(sql.WRITE_REMINDER(type_, short_type, text, user_id, timestamp))

        case 'notes':
            await database.change(sql.WRITE_NOTE(type_, short_type, text, user_id))


async def view_all_entities(telegram_id: int,
                            database: Database,
                            type_: str,
                            **timestamp) -> tuple:
    '''Возвращает текст всех сущностей из таблицы'''

    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    user_id = await check_user_id(telegram_id, database)
    short_type: str = type_[:-1]
    final_str = ''
    counter = 1
    
    match type_:
        
        case 'reminders':
            assert timestamp, "Timestamp не определен"
            raw_data = await database.view(sql.VIEW_REMINDERS(short_type, type_, user_id))
        
        case 'notes':
            raw_data = await database.view(sql.VIEW_NOTES(short_type, type_, user_id))

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
                        type_: str) -> None | int:
    
    '''Удаляет выбранную сущность пользователя.'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    user_id = await check_user_id(telegram_id, database)
    entities_list = await check_entity_id(telegram_id, database, type_='notes')
    await database.change(sql.DEL_ENTITY(type_, user_id, entities_list, index))


async def delete_all_entities(telegram_id: int, database: Database, type_:str) -> None:
    '''Удаляет все сущности пользователя.'''
    user_id = await check_user_id(telegram_id, database)
    await database.change(sql.DEL_ALL(type_, user_id))
    
# Передавать "'текст'" в write_entity
