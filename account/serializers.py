from .models import CustomUser
from rest_framework import serializers
from cloudinary.utils import cloudinary_url

class CustomUserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "profile_image", "bio", "prefecture",
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
