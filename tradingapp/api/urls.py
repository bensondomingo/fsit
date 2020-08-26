from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tradingapp.api.views import OrderAPIViewSet, StockAPIViewSet

router = DefaultRouter()
router.register('orders', OrderAPIViewSet, basename='order')
router.register('stocks', StockAPIViewSet, basename='stock')

urlpatterns = [
    path('', include(router.urls))
]
