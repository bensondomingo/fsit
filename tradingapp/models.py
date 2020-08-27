from django.db import models
from profiles.models import Profile


class Stock(models.Model):
    name = models.CharField(max_length=10, unique=True, primary_key=True)
    price = models.FloatField()

    # Added fields
    quantity = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name}: {self.price}'

    @property
    def is_avaliable(self):
        return self.quantity != 0


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell')
    ]
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES)
    trader = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='orders')
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField(default=1)
    amount = models.FloatField()
    status = models.CharField(
        max_length=10, blank=True, null=True, default='success')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.trader.user.username}: {self.stock} - {self.order_type}'

    @property
    def price_per_share(self):
        return self.amount / self.quantity

    @property
    def current_order_amount(self):
        return self.stock.price * self.quantity

    @property
    def projected_gain(self):
        if self.order_type == 'sell':
            return None
        return self.stock.price * self.quantity - self.amount
