import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")

async def postgres_do_change(query) -> None:
    try:
        # соединение с БД
        connection = await asyncpg.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB_NAME,
        )

        await connection.execute(query)
        
    except Exception as _ex:
        print('[INFO] Ошибка: ', _ex)


    finally:
        if connection:
            await connection.close()


async def postgres_do_view(query) -> str:
    try:
        # соединение с БД
        connection = await asyncpg.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB_NAME
        )
        data = await connection.fetch(query)

    except Exception as _ex:
        print('[INFO] Ошибка:', _ex)

    finally:
        if connection:
            await connection.close()
            return data
