from django.http import QueryDict
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from tradingapp.models import Order, Stock
from tradingapp.api.serializers import OrderSerializer, StockSerializer


class OrderAPIViewSet(GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin):

    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(trader=self.request.user.profile)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, QueryDict):
            data = data.copy()  # mutable
        quantity = int(data.get('quantity'))
        stock_id = data.get('stock')

        if isinstance(stock_id, int):
            stock_obj = get_object_or_404(Stock, id=data.get('stock'))
        else:
            stock_obj = get_object_or_404(Stock, name=data.get('stock'))

        profile_obj = request.user.profile
        data.update({
            'trader': profile_obj.id,
            'amount': quantity * stock_obj.price,
            'stock': stock_obj.id
        })

        s = OrderSerializer(data=data)
        if not s.is_valid():
            raise ValidationError(detail=s.errors)

        if data.get('order_type') == 'buy':
            # Reduce trader's balance by order amount.
            profile_obj.balance -= data.get('amount')
            profile_obj.save()
            # Reduce stock quantity by order quantity
            stock_obj.quantity -= quantity
            stock_obj.save()
        else:
            # Add the sell order amount to the trader's balance
            profile_obj.balance += data.get('amount')
            profile_obj.save()
            # Return the stocks quantity
            stock_obj.quantity += quantity
            stock_obj.save()

        order = s.create(s.validated_data)
        s = OrderSerializer(order)

        return Response(s.data, status=status.HTTP_201_CREATED)


class StockAPIViewSet(GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin):

    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    queryset = Stock.objects.all()
