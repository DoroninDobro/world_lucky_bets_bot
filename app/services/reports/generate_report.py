from datetime import date

from app.models import BetItem


async def generate_report(month: int, year: int):
    bets_log = await BetItem\
        .filter(worker_thread__work_thread__start_gte=date(year, month, 1))\
        .prefetch_related("worker_thread", "worker_thread__worker").all()
