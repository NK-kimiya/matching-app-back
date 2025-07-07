from pyexpat import model
from django.conf import settings
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from cloudinary.models import CloudinaryField

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    #profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    profile_image = CloudinaryField('image', blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    prefecture = models.CharField(max_length=100, null=True, blank=True)
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class UserChatRoom(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user'
    )
    
    def __str__(self):
        return f"{self.user.username}'s chat room"

class ChatMessage(models.Model):
    chat_room = models.ForeignKey(UserChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
    
class UserRoomParticipation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(UserChatRoom, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'chat_room')  # 同じ組み合わせは1つだけ

    def __str__(self):
        return f"{self.user.username} in room of {self.chat_room.user.username}"