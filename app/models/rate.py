from tortoise import fields
from tortoise.models import Model

DECIMAL_CONFIG = dict(max_digits=12, decimal_places=4)


class RateItem(Model):
    id = fields.IntField(pk=True)
    at = fields.DateField(auto_now=True)
    currency = fields.CharField(max_length=16)
    to_eur = fields.DecimalField(**DECIMAL_CONFIG)
    to_usd = fields.DecimalField(**DECIMAL_CONFIG)

    class Meta:
        table = "historical_rates"
        unique_together = (("at", "currency"),)

    def __repr__(self):
        return f"<RateItem id={self.id}>"
