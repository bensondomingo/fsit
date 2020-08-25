from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Every registered user has a Profile. The idea is that the User model
    will be used for authentication purposes. The Profile model will be used
    to hold trading records. A new Profile object will be created and binded
    during user registration.
    """
    balance = models.FloatField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
