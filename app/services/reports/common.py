from app.models import BetItem, RateItem


async def get_mont_bets(date_range):
    return await BetItem \
        .filter(worker_thread__work_thread__start__gte=date_range.start) \
        .filter(worker_thread__work_thread__start__lt=date_range.stop) \
        .prefetch_related("bookmaker", "worker_thread", "worker_thread__work_thread", "worker_thread__worker").all()


async def get_month_rates(date_range):
    rates = await RateItem \
        .filter(at__gte=date_range.start.date()) \
        .filter(at__lte=date_range.stop.date()) \
        .order_by("at")
    result = {}
    for rate in rates:
        try:
            result[rate.at][rate.currency] = rate
        except KeyError:
            result[rate.at] = {rate.currency: rate}
    return result
