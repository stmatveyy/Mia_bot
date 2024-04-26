from typing import Any
from dataclasses import dataclass

# Модуль с командами SQL для упрощения чтения кода

def _user_id_(t_td: int) -> str:
    return f'SELECT "id" FROM "public.users" WHERE "telegram_id"={t_td}'


def _entity_id_(type_: str, user_id: int) -> str:
    return f'SELECT "id" FROM "public.{type_}" WHERE "fk_user_{type_[:-1]}"={user_id}'


def _write_reminder_(type_: str,
                        short_type: str,
                        text: str,
                        user_id: int,
                        timestamp: int) -> str:
    
    return f'INSERT INTO "public.{type_}" ({short_type}_text, fk_user_{short_type}, time_stamp) VALUES ({text}, {user_id}, TIMESTAMP \'{timestamp}\')'


def _write_note_(type_: str,
                    short_type: str,
                    text: str,
                    user_id: int) -> str:
    
    return f'INSERT INTO "public.{type_}"({short_type}_text, fk_user_{short_type}) VALUES ({text}, {user_id})'


def _view_reminders_(short_type: str,
                        type_: str,
                        user_id: int) -> str:
    
    return f'SELECT "{short_type}_text", time_stamp FROM "public.{type_}" WHERE "fk_user_{short_type}"={user_id}'


def _view_notes_(short_type: str,
                      type_: str,
                      user_id: int) -> str:
    
    return f'SELECT "{short_type}_text" FROM "public.{type_}" WHERE "fk_user_{short_type}"={user_id}'


def _del_(type_: str,
                user_id: int,
                entities_list: list,
                index: int) -> str:
    
    return f'DELETE FROM "public.{type_}" WHERE "fk_user_{type_[:-1]}"={user_id} AND id = {entities_list[index-1]}'


def _del_all_(type_: str,
                    user_id: int) -> str:
    return f'DELETE FROM "public.{type_}" WHERE "fk_user_{type_[:-1]}"={user_id}'


def _check_num_(num: int) -> str:
    return f'SELECT * FROM "public.users" WHERE number = {int(str(num)[0:])}'


def _register_user_(message, num) -> str:
    return f'UPDATE public."public.users" SET telegram_id = {message.from_user.id} WHERE number = {int(str(num)[0:])}'


@dataclass(frozen=True)
class Queries():
    USER_ID: Any        = _user_id_
    ENTITY_ID: Any      = _entity_id_
    WRITE_REMINDER: Any = _write_reminder_
    WRITE_NOTE: Any     = _write_note_
    VIEW_REMINDERS: Any = _view_reminders_
    VIEW_NOTES: Any     = _view_notes_
    DEL_ENTITY: Any     = _del_
    DEL_ALL: Any        = _del_all_
    CHECK_NUM: Any      = _check_num_
    REG_USER: Any       = _register_user_

SQL_queries = Queries()




