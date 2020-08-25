from rest_framework.serializers import ModelSerializer

from tradingapp.models import Order, Stock


class StockSerializer(ModelSerializer):

    class Meta:
        model = Stock
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    stock = StockSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
