from tortoise.transactions import in_transaction

from app.models import SendWorkers, WorkerInThread


async def create_send_workers(users, additional_text, using_db=None):
    sw = []
    for user in users:
        sw.append(await SendWorkers.create(worker=user, text=additional_text, using_db=using_db))
        await sw[-1].fetch_related("worker", using_db=using_db)
    return sw


async def get_workers(additional_text):
    async with in_transaction() as conn:
        previous_workers = await additional_text \
            .send_to_workers \
            .all() \
            .prefetch_related("worker")

        previous_users = [worker.worker for worker in previous_workers]
        thread = await additional_text.thread

        new_workers = await thread \
            .workers \
            .filter(worker__id__not_in=[user.id for user in previous_users]) \
            .prefetch_related("worker") \
            .all()
        sw = await create_send_workers([worker.worker for worker in new_workers], additional_text, conn)
        actual_workers = [*previous_workers, *sw]
    return actual_workers


async def get_enable_workers(additional_text):
    thread = await additional_text.thread
    send_to_workers = await get_workers(additional_text)
    enable_workers = [send_to_worker for send_to_worker in send_to_workers if send_to_worker.send]
    users = [await send_to_worker.worker for send_to_worker in enable_workers]
    wits = [await WorkerInThread.get(worker=user, work_thread=thread) for user in users]
    return list(zip(users, [wit.message_id for wit in wits]))


async def get_disable_workers(additional_text):
    send_to_workers = await get_workers(additional_text)
    disable_workers = [send_to_worker for send_to_worker in send_to_workers if not send_to_worker.send]
    users = [await send_to_worker.worker for send_to_worker in disable_workers]
    return users


async def change_disinformation(additional_text, is_disinformation):
    additional_text.is_disinformation = is_disinformation
    await additional_text.save()


async def change_worker(worker_id, enable):
    await SendWorkers.filter(id=worker_id).update(send=enable)
