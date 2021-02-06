from app.models import WorkThread, WorkerInThread
from app.models.statistic.thread_users import ThreadUsers
from app.services.collections_utils import get_first_dict_value
from app.services.datetime_utils import get_moth_range, date_to_datetime


async def generate_thread_users(month: int, year: int) -> list[ThreadUsers]:
    loaded_data = await load_thread_users(month, year)
    users = {
        user_id: worker_in_thread.worker
        for inner in loaded_data.values()
        for user_id, worker_in_thread in inner.items()
    }
    user_names = {user_id: user.fullname for user_id, user in users.items()}
    thread_users = []
    for thread_id, workers in loaded_data.items():
        thread: WorkThread = get_first_dict_value(workers).work_thread
        assert thread.id == thread_id, "Must be equals, it writhed so that it is equals. if not, you fail refactoring:)"
        has_worked = []
        for user_id in user_names:
            has_worked.append(True if user_id in workers else False)
        thread_users.append(ThreadUsers(
            day=thread.start.date(),
            id=thread.id,
            user_names=list(user_names.values()),
            user_has_worked=has_worked
        ))
    return thread_users


async def load_thread_users(month: int, year: int) -> dict[int, dict[int, WorkerInThread]]:
    monthly_threads = await get_mont_threads(month, year)
    users_statistics = {}
    for thread in monthly_threads:
        workers: list[WorkerInThread] = thread.workers  # noqa
        for worker in workers:
            try:
                users_statistics[thread.id][worker.worker.id] = worker
            except KeyError:
                users_statistics[thread.id] = {worker.worker.id: worker}
    return users_statistics


async def get_mont_threads(month, year) -> list[WorkThread]:
    date_start, date_stop = get_moth_range(month, year)
    return await WorkThread \
        .filter(start__gte=date_to_datetime(date_start)) \
        .filter(start__lte=date_to_datetime(date_stop)) \
        .prefetch_related(
            "workers",
            "workers__worker",
            "workers__work_thread",
        ).all()
