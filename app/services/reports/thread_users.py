from app.models import WorkThread
from app.models.statistic.thread_users import ThreadUsers
from app.services.collections_utils import get_first_dict_value
from app.models.data_range import date_to_datetime


async def generate_thread_users(date_range):
    loaded_data = await load_thread_users(date_range)
    users = {
        user_id: worker_in_thread.worker
        for inner in loaded_data.values()
        for user_id, worker_in_thread in inner.items()
    }
    user_names = {user_id: user.fullname for user_id, user in users.items()}
    thread_users = []
    for thread_id, workers in loaded_data.items():
        thread = get_first_dict_value(workers).work_thread
        assert thread.id == thread_id, "Must be equals, it writhed so that it is equals. if not, you fail refactoring:)"
        has_worked = []
        for user_id in user_names:
            has_worked.append(True if user_id in workers else False)
        thread_users.append(ThreadUsers(
            day=thread.start.date(),
            thread=thread,
            user_names=list(user_names.values()),
            user_has_worked=has_worked
        ))
    return thread_users


async def load_thread_users(date_range):
    monthly_threads = await get_mont_threads(date_range)
    users_statistics = {}
    for thread in monthly_threads:
        workers = thread.workers
        for worker in workers:
            try:
                users_statistics[thread.id][worker.worker.id] = worker
            except KeyError:
                users_statistics[thread.id] = {worker.worker.id: worker}
    return users_statistics


async def get_mont_threads(date_range):
    return await WorkThread \
        .filter(start__gte=date_to_datetime(date_range.start)) \
        .filter(start__lte=date_to_datetime(date_range.stop)) \
        .prefetch_related(
            "workers",
            "workers__worker",
            "workers__work_thread",
        ).all()
