from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tradingapp.models import Order, Stock


class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    quantity = serializers.FloatField(min_value=1)

    class Meta:
        model = Order
        fields = '__all__'

    def validate(self, attrs):
        stock = attrs.get('stock')
        trader = attrs.get('trader')

        if attrs.get('order_type') == 'sell':
            if attrs.quantity > stock.available_shares:
                raise ValidationError(
                    f'Not enough stock! Available: {stock.available_shares}')
        else:
            if attrs.get('amount') > trader.balance:
                raise ValidationError('Not enough balance.')
            if attrs.get('quantity') > stock.quantity:
                raise ValidationError(
                    f'Not enough stock! Available: {stock.quantity}')
        return super().validate(attrs)
