import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DB_NAME = os.getenv("DB_NAME")

query = ''''''
async def postgres_do_change(query):
    try:
        # соединение с БД
        connection = psycopg2.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB_NAME
        )
        # автокомит почему-то не работает, каждый раз писать connetion.commit()

        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
            print('[INFO] Запрос выполнен успешно!')

    except Exception as _ex:
        print('[INFO] Упс! База данных наебнулась...', _ex)
        connection.rollback()  # полный откат изменений, если что-то пошло не так

    finally:
        if connection:
            connection.close()
            print('[INFO] База данных выключилась')

def postgres_do_view(query) -> any:
    try:
        # соединение с БД
        connection = psycopg2.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB_NAME
        )
        # автокомит почему-то не работает, каждый раз писать connetion.commit()
        with connection.cursor() as cursor:
            cursor.execute(query)
            print('[INFO] Запрос выполнен успешно!')
            return cursor.fetchall()
            
    except Exception as _ex:
        print('[INFO] Упс! База данных наебнулась...', _ex)
        connection.rollback()  # полный откат изменений, если что-то пошло не так

    finally:
        if connection:
            connection.close()
            print('[INFO] База данных выключилась')
