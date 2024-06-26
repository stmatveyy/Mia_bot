import asyncpg
from config_data.config import config
from typing import Any
import logging

HOST = config.db.host
USER = config.db.user
PASSWORD = config.db.password
DB_NAME = config.db.db_name


class Database():
    pool = None

    def __init__(self) -> None:
        pass

    async def _ainit_(self):
        self.pool = await asyncpg.create_pool(host=HOST,
                                              user=USER,
                                              password=PASSWORD,
                                              database=DB_NAME,
                                              min_size=10,
                                              max_size=100,
                                              max_queries=10,
                                              max_inactive_connection_lifetime=0
                                              )

    async def change(self, query: str) -> None:
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(query)

        except Exception as _ex:
            logging.fatal(f'Ошибка: {_ex}')

    async def view(self, query: str) -> Any:
        try:
            async with self.pool.acquire() as connection:
                data = await connection.fetch(query)
                return data

        except Exception as _ex:
            logging.fatal(f'Ошибка: {_ex}')

    async def close(self) -> None:
        await self.pool.close()
