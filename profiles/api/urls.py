from django.urls import path
from profiles.api.views import ProfileAPIView

urlpatterns = [
    path('profiles/<int:pk>/', ProfileAPIView.as_view(), name='profile')
]
