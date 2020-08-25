from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tradingapp.api.views import OrderAPIViewSet

router = DefaultRouter()
router.register('')
router.register('order', OrderAPIViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls))
]
