import asyncio
from contextlib import suppress

from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from app import config, keyboards as kb
from app.models import WorkThread, AdditionalText, RateItem
from app.models.db.work_thread import check_thread_running
from app.services.additional_text import (
    get_enable_workers,
    create_send_workers,
    get_workers
)
from app.services.msg_cleaner_on_fail import msg_cleaner
from app.services.rates import OpenExchangeRates


async def start_new_thread(photo_file_id, admin, bot):
    async with in_transaction() as connection, \
               msg_cleaner() as transaction_messages:
        created_thread = WorkThread(start_photo_file_id=photo_file_id,
                                    admin_id=admin.id)
        await created_thread.save(using_db=connection)

        msg_to_workers = await bot.send_photo(
            chat_id=config.WORKERS_CHAT_ID,
            photo=photo_file_id,
            caption=f"{created_thread.id}",
            reply_markup=kb.get_agree_work(created_thread.id)
        )
        transaction_messages.append(msg_to_workers)

        msg_to_admin = await bot.send_photo(
            chat_id=admin.id,
            photo=photo_file_id,
            caption=f"{created_thread.id}. Message sent",
            reply_markup=kb.get_work_thread_admin_kb(created_thread.id)
        )
        transaction_messages.append(msg_to_admin)

        created_thread.start_message_id = msg_to_admin.message_id
        created_thread.workers_chat_message_id = msg_to_workers.message_id
        await created_thread.save(using_db=connection)

    await save_daily_rates()

    return created_thread


async def save_daily_rates(using_db=None):
    async with OpenExchangeRates(config.OER_TOKEN) as oer:
        with suppress(IntegrityError):
            for currency in config.currencies:
                rate = RateItem(
                    at=(await oer.get_updated_date()).date(),
                    currency=currency,
                    to_eur=await oer.get_rate("EUR", currency),
                    to_usd=await oer.get_rate("USD", currency),
                )
                await rate.save(using_db=using_db)


async def get_thread(message_id):
    return await WorkThread.get(start_message_id=message_id)


@check_thread_running
async def add_info_to_thread(text, *, thread):
    async with in_transaction() as connection:
        a_t = await AdditionalText.create(text=text, thread=thread,
                                          using_db=connection)
        workers = await create_send_workers(
            await get_workers_from_thread(thread=thread),
            a_t, using_db=connection
        )
    return a_t, workers


async def stop_thread(thread_id):
    async with in_transaction() as connection:
        thread = await WorkThread.get(id=thread_id)
        thread.stopped = True
        await thread.save(using_db=connection)
        return thread


@check_thread_running
async def start_mailing(a_text, bot, *, thread):
    async with in_transaction() as conn, msg_cleaner() as transaction_messages:
        enable_workers = await get_enable_workers(a_text)
        for enable_worker, worker_start_thread_message_id in enable_workers:
            msg = await bot.send_message(
                chat_id=enable_worker.id,
                text=a_text.text,
                reply_to_message_id=worker_start_thread_message_id,
            )
            transaction_messages.append(msg)
            await asyncio.sleep(0.1)
        enable_workers_user = [worker for worker, _ in enable_workers]

        if a_text.is_disinformation:
            disinformation_log_msg_text = await render_disinformation_log(
                a_text,
                enable_workers_user,
                [worker.worker for worker in await get_workers(a_text)]
            )
            disinformation_log_msg = await bot.send_message(
                chat_id=config.USER_LOG_CHAT_ID,
                text=disinformation_log_msg_text,
            )
            transaction_messages.append(disinformation_log_msg)

        a_text.is_draft = False
        await a_text.save(using_db=conn)


async def render_disinformation_log(a_text, enable_workers, all_workers, ):
    text_parts = [
        f"Match <b>{a_text.get_thread_id()}</b>",
        f"Message: <b>{a_text.text}</b>",
    ]
    if enable_workers:
        text_parts.append("Received privately:")
        for enable_worker in enable_workers:
            text_parts.append(enable_worker.mention_link)
    if all_workers:
        text_parts.append("Total participated at the time of sending:")
        for worker in all_workers:
            text_parts.append(worker.mention_link)
    else:
        text_parts.append("There were no participants at the time of sending")
    return "\n".join(text_parts)


@check_thread_running
async def get_workers_from_thread(*, thread):
    workers_in_thread = await thread.workers
    if workers_in_thread:
        return [await worker.worker for worker in workers_in_thread]
    else:
        return []


async def thread_not_found(callback_query, thread_id):
    await callback_query.answer(f"Match thread_id={thread_id} not found",
                                show_alert=True)
    await callback_query.message.edit_caption(
        f"Match thread_id={thread_id} not found, "
        f"maybe it was already finished",
        reply_markup=kb.get_stopped_work_thread_admin_kb(thread_id),
    )


async def rename_thread(thread_id, new_name):
    thread = await WorkThread.get(id=thread_id)
    thread.name = new_name
    await thread.save()


async def send_notification_stop(thread, bot):
    for worker in await thread.workers:
        user = await worker.worker
        await bot.send_message(user.id, f"Match {thread.id} is over",
                               reply_to_message_id=worker.message_id)
        await asyncio.sleep(0.5)
    notify_text = (
        f"{thread.id}. "
        f"Match {thread.name if thread.name is not None else ''} "
        f"has been successfully completed"
    )
    await bot.send_message(
        chat_id=config.USER_LOG_CHAT_ID,
        text=notify_text,
    )
