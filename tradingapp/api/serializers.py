from django.db.models import Sum
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tradingapp.models import Order, Stock


class StockSerializer(serializers.ModelSerializer):
    invested = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = '__all__'

    def get_invested(self, instance):
        trader = self.context['request'].user.profile
        buy = trader.orders.filter(order_type='buy', stock=instance)
        if buy.count() == 0:
            return None
        sell = trader.orders.filter(order_type='sell', stock=instance)

        buy_amount = buy.aggregate(Sum('amount')).get('amount__sum')
        bought_shares = buy.aggregate(Sum('quantity')).get('quantity__sum')
        if sell.count() == 0:
            sell_amount = 0
            sold_shares = 0
        else:
            sell_amount = sell.aggregate(Sum('amount')).get('amount__sum')
            sold_shares = sell.aggregate(Sum('quantity')).get('quantity__sum')
        return {
            'buy': {
                'amount': buy_amount,
                'shares': bought_shares
            },
            'sell': {
                'amount': sell_amount,
                'shares': sold_shares
            },
            'net_invested': buy_amount - sell_amount,
            'net_shares': bought_shares - sold_shares
        }


class OrderSerializer(serializers.ModelSerializer):
    quantity = serializers.FloatField(min_value=1)
    price_per_share = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_price_per_share(self, instance):
        return instance.price_per_share

    def validate(self, attrs):
        """
        Perform extra validation aside from field level validation.
        """
        trader = attrs.get('trader')
        stock = attrs.get('stock')

        if attrs.get('order_type') == 'sell':
            # Get total shares owned by the trader
            bought_shares = trader.orders.filter(
                order_type='buy',
                stock__name=stock.name).aggregate(
                    Sum('quantity')).get('quantity__sum')
            if bought_shares is None:
                raise ValidationError("You don't have any shares to sell.")

            sold_shares = trader.orders.filter(
                order_type='sell',
                stock__name=stock.name).aggregate(
                    Sum('quantity')).get('quantity__sum')
            bought_shares = bought_shares if bought_shares is not None else 0
            sold_shares = sold_shares if sold_shares is not None else 0

            # Ensure only available shares can be sold
            availble_shares = bought_shares - sold_shares
            if attrs.get('quantity') > availble_shares:
                raise ValidationError(
                    (f'Not enough stocks to sell. Available {stock.name} '
                     f'shares: {bought_shares}'))
        else:
            if attrs.get('amount') > trader.balance:
                raise ValidationError('Not enough balance')
            if attrs.get('quantity') > stock.quantity:
                raise ValidationError(
                    f'Not enough stock! Available: {stock.quantity}')
        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['trader'] = str(instance.trader)
        return ret
