from .models import CustomUser,UserChatRoom
from rest_framework import serializers
from cloudinary.utils import cloudinary_url
from .models import ChatMessage

class CustomUserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    chat_rooms = serializers.SerializerMethodField()  # 👈 追加
    
    class Meta:
        model = CustomUser
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "profile_image", "bio", "prefecture","chat_rooms",
        ]

    def get_profile_image(self, obj):
        if not obj.profile_image:
            return None

        # 👇 version 指定は削除する
        url, _ = cloudinary_url(
            obj.profile_image.public_id,
            format=obj.profile_image.format,
            secure=True,
            invalidate=True  # ← オプション
        )
        return url
    
    def get_prefecture(self, obj):
        return obj.prefecture.name if obj.prefecture else None
    
    def get_chat_rooms(self, obj):
        rooms = UserChatRoom.objects.filter(user=obj)
        return UserChatRoomSerializer(rooms, many=True).data
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'profile_image', 'bio', 'prefecture')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_image=validated_data.get('profile_image'),
            bio=validated_data.get('bio'),
            prefecture=validated_data.get('prefecture'),
        )
        return user

class UserChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChatRoom
        fields = ['id']  # 必要に応じて変更
class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)  # 👈 これを追加！
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_room', 'sender', 'sender_username', 'content', 'timestamp']