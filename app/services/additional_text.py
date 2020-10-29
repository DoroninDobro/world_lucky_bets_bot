import typing

from app.models import AdditionalText, User, SendWorkers, WorkerInThread


async def create_send_workers(
        users: typing.List[User],
        additional_text: AdditionalText,
        using_db=None
) -> typing.List[SendWorkers]:
    sw = []
    for user in users:
        sw.append(await SendWorkers.create(worker=user, text=additional_text, using_db=using_db))
        await sw[-1].fetch_related("worker", using_db=using_db)
    return sw


async def get_workers(additional_text: AdditionalText):
    return await additional_text.send_to_workers.all().prefetch_related("worker")


async def get_enable_workers(additional_text: AdditionalText) -> typing.Iterable[typing.Tuple[User, int]]:
    thread = await additional_text.thread
    send_to_workers = await additional_text.send_to_workers.filter(send=True).all()
    users = [await send_to_worker.worker for send_to_worker in send_to_workers]
    wits = [await WorkerInThread.get(worker=user, work_thread=thread) for user in users]
    return list(zip(users, [wit.message_id for wit in wits]))


async def get_disable_workers(additional_text: AdditionalText) -> typing.Iterable[User]:
    send_to_workers = await additional_text.send_to_workers.filter(send=False).all()
    users = [await send_to_worker.worker for send_to_worker in send_to_workers]
    return users


async def change_disinformation(additional_text: AdditionalText, is_disinformation: bool):
    additional_text.is_disinformation = is_disinformation
    await additional_text.save()


async def change_worker(worker_id: int, enable: bool):
    worker = await SendWorkers.get(id=worker_id)
    worker.send = enable
    await worker.save()
    return worker
