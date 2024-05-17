import redis.asyncio as redis

# class to initialise Redis connection pool
class RedisPool():
    
    def __init__(self) -> None:
        ...

    async def __ainit__(self) -> None:
        self.pool = redis.ConnectionPool.from_url("redis://localhost")
        self.client = redis.Redis.from_pool(self.pool)
        