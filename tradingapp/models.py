from django.db import models
from profiles.models import Profile


class Stock(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()

    # Added fields
    quantity = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.name} - {self.price}'

    def is_avaliable(self):
        return self.quantity != 0


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell')
    ]
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES)
    trader = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='order')
    stock = models.OneToOneField(
        Stock, on_delete=models.CASCADE, related_name='stock')
    quantity = models.IntegerField(default=1)
    amount = models.FloatField()
    status = models.CharField(
        max_length=10, blank=True, null=True, default='success')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.trader.username}: {self.stock} - {self.order_type}'

    def price_per_quntity(self):
        return self.amount * self.quantity

    def projected_gain(self):
        pass
