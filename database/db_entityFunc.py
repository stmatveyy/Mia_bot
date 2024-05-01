from database.database_func import Database
from misc.SQL_dict import SQL_queries as sql
from typing import Any
import logging
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
    raw_data = await database.view(sql.ENTITY_ID(type_, user_id))
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

async def write_job_id(database: Database,
                                telegram_id,
                                redis_job_id) -> None:
    '''Записывает id таска в Postgres'''
    user_id = await check_user_id(database=database, telegram_id=telegram_id)
    await database.change(f'UPDATE "public.reminders" SET redis_id = \'{redis_job_id}\' WHERE id = (SELECT MAX(id) FROM "public.reminders" WHERE fk_user_reminder = {user_id})')

async def view_all_job_ids(database: Database,
                           telegram_id: int) -> dict[str:int]:
    '''Возвращает список всех id задач пользователя'''
    user_id = await check_user_id(database=database, telegram_id=telegram_id)
    raw_redis_ids =  await database.view(f'SELECT redis_id, time_stamp FROM "public.reminders" WHERE fk_user_reminder = {user_id}')
    return {record['redis_id']:record['time_stamp'] for record in raw_redis_ids}


async def view_all_entities(telegram_id: int,
                            database: Database) -> tuple:
    '''Возвращает текст всех сущностей из таблицы'''

    user_id = await check_user_id(telegram_id, database)

    final_str = ''

    raw_reminders = await database.view(sql.VIEW_REMINDERS('reminder', 'reminders', user_id))
    raw_notes = await database.view(sql.VIEW_NOTES('note', 'notes', user_id))
    counter = 1
    notes_counter = 0
    rem_counter = 0

    if raw_notes is None and raw_reminders is None:
        return 0
    
    else:
        
        if raw_reminders != []:
            final_str += '<b>\nТвои Напоминания:\n</b>'    
            for el in raw_reminders:
                width = 15 - len(el['reminder_text'])
                final_str += '<b>'+ str(counter) + ':</b> <i>' + el['reminder_text'] + '</i> ' + "-" *width + ' <b>' +\
                               str(el['time_stamp'].date().day) + "." + str(el['time_stamp'].date().month) + \
                                  " " + str(el['time_stamp'].hour) + ":00" '</b>\n'
                counter +=1
                rem_counter += 1

        
        if raw_notes != []:

            final_str += '<b>\nТвои заметки: \n</b>'
            for el in raw_notes:
                final_str += '<b>' + (str(counter) + ':</b> <i>' + el[0] + '</i>\n')
                counter +=1
                notes_counter += 1

        return final_str, counter, rem_counter, notes_counter

async def delete_entity(telegram_id: int,
                        index: int,
                        database: Database,
                        type_: str) -> None | str:
    
    '''Удаляет выбранную сущность пользователя и возвращает redis_id в случае напоминаний'''
    assert type_ in allowed_types, f"Типа сущности не существует, разрешенные типы: {allowed_types}"
    user_id = await check_user_id(telegram_id, database)
    entities_list = await check_entity_id(telegram_id, database, type_=type_)
    
    redis_id_record = await database.view(f'SELECT redis_id FROM "public.reminders" WHERE id = {entities_list[index-1]}')
    logging.debug(f'FR0M {__name__}: notifications list: {entities_list}, user_id: {user_id}, supposed id: {entities_list[index-1]}')
    await database.change(sql.DEL_ENTITY(type_=type_, user_id=user_id, entities_list=entities_list, index=index))
    return redis_id_record[0]['redis_id'] if redis_id_record else None


async def delete_all_entities(telegram_id: int, database: Database, type_:str) -> None:
    '''Удаляет все сущности пользователя.'''
    user_id = await check_user_id(telegram_id, database)
    await database.change(sql.DEL_ALL(type_, user_id))
    
# Передавать "'текст'" в write_entity
