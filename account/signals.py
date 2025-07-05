from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserChatRoom

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_chat_room(sender, instance, created, **kwargs):
    if created:
        UserChatRoom.objects.create(user=instance)