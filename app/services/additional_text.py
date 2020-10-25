import typing

from app.models import AdditionalText, WorkThread, User, SendWorkers, WorkerInThread


async def new_additional_text(text: str, tread: WorkThread):
    return await AdditionalText.create(text=text, thread=tread)


async def create_send_workers(users: typing.List[User], additional_text: AdditionalText) -> typing.List[SendWorkers]:
    sw = []
    for user in users:
        sw.append(await SendWorkers.create(worker=user, text=additional_text))
        await sw[-1].fetch_related("worker")
    return sw


async def mark_additional_text_as_send(additional_text: AdditionalText):
    additional_text.is_draft = False
    await additional_text.save()


async def get_workers(additional_text: AdditionalText):
    return await additional_text.send_to_workers.all().prefetch_related("worker")


async def get_enable_workers(additional_text: AdditionalText):
    thread = await additional_text.thread
    send_to_workers = await additional_text.send_to_workers.filter(send=True).all()
    users = [await send_to_worker.worker for send_to_worker in send_to_workers]
    wits = [await WorkerInThread.get(worker=user, work_thread=thread) for user in users]
    return zip(users, [wit.message_id for wit in wits])


async def change_disinformation(additional_text: AdditionalText, is_disinformation: bool):
    additional_text.is_disinformation = is_disinformation
    await additional_text.save()


async def change_worker(worker: SendWorkers, enable: bool):
    worker.send = enable
    await worker.save()
