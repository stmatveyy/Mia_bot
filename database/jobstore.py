from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from uuid import uuid4

jobstores = {
    'redis': RedisJobStore(host='localhost', port=6379, db=0)
}
scheduler = AsyncIOScheduler(jobstores=jobstores)

def add_user_job(user_id:int, job_function:callable, scheduler: AsyncIOScheduler, trigger, *args, **kwargs) -> str:
    '''Добавляет задачу в Redis, возвращает ее id'''
    
    job_number = str(uuid4())
    job_id = f"user_{user_id}_{job_function.__name__}_{job_number}"
    scheduler.add_job(func=job_function, trigger=trigger, id=job_id, jobstore='redis', args=args, kwargs=kwargs['kwargs'] )
    return job_id


