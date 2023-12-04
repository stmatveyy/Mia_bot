from database import database_func
import asyncio

async def check_user_id(telegram_id:int) -> int:
    res = await database_func.postgres_do_view(f'SELECT "id" FROM "public.users" WHERE "telegram_id"={telegram_id}')
    return int(res[0][0])

async def check_notes_id(telegram_id:int) -> list[int]:
    user_id = await check_user_id(telegram_id)
    final_list = []
    raw_data = await database_func.postgres_do_view(f'SELECT "id" FROM "public.notes" WHERE "fk_user_note"={user_id}')
    for el in raw_data:
        final_list.append(el[0])
    return final_list



async def write_note(note_text: str, telegram_id: int) -> None:
    user_id = await check_user_id(telegram_id)
    await database_func.postgres_do_change(f'INSERT INTO "public.notes"(note_text, fk_user_note) VALUES ({note_text}, {user_id})')

async def view_all_notes(telegram_id:int) -> str | int:
    user_id = await check_user_id(telegram_id)
    final_str = ''
    counter = 1
    raw_data = await database_func.postgres_do_view(f'SELECT "note_text" FROM "public.notes" WHERE "fk_user_note"={user_id}')
    if raw_data == []:
        return 0
    else:
        for el in raw_data:
            final_str += (str(counter) + ': <i>' + el[0].strip() + '</i>\n')
            counter += 1
        return final_str,counter


async def delete_note(telegram_id:int, note_index:int) -> None | int:
    user_id = await check_user_id(telegram_id)
    notes_list = await check_notes_id(telegram_id)
    await database_func.postgres_do_change(f'DELETE FROM "public.notes" WHERE "fk_user_note"={user_id} AND id = {notes_list[note_index-1]}')

async def delete_all_notes(telegram_id:int) -> None:
    user_id = await check_user_id(telegram_id)
    await database_func.postgres_do_change(f'DELETE FROM "public.notes" WHERE "fk_user_note"={user_id}')
# Передавать "'текст'" в write_note
