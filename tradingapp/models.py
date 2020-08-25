from django.db import models
from profiles.models import Profile

# Create your models here.


class Stock(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()

    # Added fields
    available_shares = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.name} - {self.price}'

    def is_avaliable(self):
        return self.available_shares != 0


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell')
    ]
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES)
    trader = models.ForeignKey(Profile, on_delete=models.CASCADE)
    stock = models.OneToOneField(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    cost = models.FloatField()
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
