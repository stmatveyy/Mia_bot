from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

jobstores = {
    'redis': RedisJobStore(host='localhost', port=6379, db=0)
}
scheduler = AsyncIOScheduler(jobstores=jobstores)
