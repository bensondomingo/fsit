from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from profiles.models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """ Create a new profile for new user instance """

    if instance.is_superuser:
        return

    if created:
        # Create a new profile for new users
        Profile.objects.create(user=instance)
