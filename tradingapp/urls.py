from django.urls import path, include

urlpatterns = [
    path('api/', include('tradingapp.api.urls')),
]
