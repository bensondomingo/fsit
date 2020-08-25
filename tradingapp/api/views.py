from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from tradingapp.models import Order
from tradingapp.api.serializers import OrderSerializer


class OrderAPIViewSet(GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin):

    class Meta:
        permission_classes = [IsAuthenticated]
        serializer_class = OrderSerializer
        queryset = Order.objects.all()

    def get_queryset(self):
        self.queryset.filter(trader=self.request.user.profile)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class StockAPIViewSet(GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin):
    pass
