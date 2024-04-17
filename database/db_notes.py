from database.database_func import Database


async def check_user_id(telegram_id: int, database: Database) -> int:
    '''Возвращает ID пользователя в базе данных.'''
    res = await database.view(query=f'SELECT "id" FROM "public.users" WHERE "telegram_id"={telegram_id}')
    return int(res[0][0])


async def check_notes_id(telegram_id: int, database: Database) -> list[int]:
    '''Возвращает список ID заметок пользователя из базы данных.'''
    user_id = await check_user_id(telegram_id, database)
    final_list = []
    raw_data = await database.view(f'SELECT "id" FROM "public.notes" WHERE "fk_user_note"={user_id}')
    for el in raw_data:
        final_list.append(el[0])
    return final_list


async def write_note(note_text: str,
                     telegram_id: int,
                     database: Database) -> None:
    '''Записывает заметку в базу данных.'''
    user_id = await check_user_id(telegram_id, database)
    await database.change(f'INSERT INTO "public.notes"(note_text, fk_user_note) VALUES ({note_text}, {user_id})')


async def view_all_notes(telegram_id: int, database: Database) -> str | int:
    '''Возвращает текст всех заметок пользователя из базы данных'''
    user_id = await check_user_id(telegram_id, database)
    final_str = ''
    counter = 1
    raw_data = await database.view(f'SELECT "note_text" FROM "public.notes" WHERE "fk_user_note"={user_id}')
    if raw_data == []:
        return 0
    else:
        for el in raw_data:
            final_str += (str(counter) + ': <i>' + el[0].strip() + '</i>\n')
            counter += 1
        return final_str, counter


async def delete_note(telegram_id: int,
                      note_index: int,
                      database: Database) -> None | int:
    '''Удаляет выбранную заметку пользователя.'''
    user_id = await check_user_id(telegram_id, database)
    notes_list = await check_notes_id(telegram_id, database)
    await database.change(f'DELETE FROM "public.notes" WHERE "fk_user_note"={user_id} AND id = {notes_list[note_index-1]}')


async def delete_all_notes(telegram_id: int, database: Database) -> None:
    '''Удаляет все заметки пользователя.'''
    user_id = await check_user_id(telegram_id, database)
    await database.change(f'DELETE FROM "public.notes" WHERE "fk_user_note"={user_id}')
# Передавать "'текст'" в write_note
