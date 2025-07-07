from .models import CustomUser,UserChatRoom
from rest_framework import serializers
from cloudinary.utils import cloudinary_url
from .models import ChatMessage

class CustomUserSerializer(serializers.ModelSerializer):
    # profile_image フィールドはデフォルトのフィールドではなく、メソッドで取得するカスタムフィールド
    profile_image = serializers.SerializerMethodField()
    # chat_rooms フィールドもメソッドで取得（UserChatRoom の一覧を含めるため）
    chat_rooms = serializers.SerializerMethodField()  # 👈 追加
    
    class Meta:
        # 対象となるモデルを指定（CustomUser モデルをシリアライズする）
        model = CustomUser
         # API で返すフィールドの一覧を指定
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "profile_image", "bio", "prefecture","chat_rooms",
        ]

    # profile_image フィールド用のメソッド（Cloudinaryの画像URLを生成）
    def get_profile_image(self, obj):
        if not obj.profile_image:
            return None# 画像が設定されていない場合は None を返す

         # Cloudinary から画像URLを取得（セキュアURLでキャッシュ無効化付き）
        url, _ = cloudinary_url(
            obj.profile_image.public_id,
            format=obj.profile_image.format,
            secure=True,
            invalidate=True  # ← オプション
        )
        return url
    
    def get_prefecture(self, obj):
        return obj.prefecture.name if obj.prefecture else None
    
     # chat_rooms フィールド用のメソッド（そのユーザーが属するチャットルームをシリアライズ）
    def get_chat_rooms(self, obj):
        rooms = UserChatRoom.objects.filter(user=obj)# ユーザーに関連するチャットルームを取得
        return UserChatRoomSerializer(rooms, many=True).data# シリアライズして返す
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)# パスワードは書き込み専用（レスポンスには含めない）

    class Meta:
        model = CustomUser# 対象となるモデルを CustomUser に設定
        fields = ('username', 'email', 'password', 'profile_image', 'bio', 'prefecture') # フォームやAPIで受け付けるフィールドを列挙

    def create(self, validated_data):# 保存処理をカスタマイズする create メソッドを定義
        user = CustomUser.objects.create_user(
            username=validated_data['username'],# ユーザー名を渡す
            email=validated_data['email'],# メールアドレスを渡す
            password=validated_data['password'], # パスワード（ハッシュ化される）
            profile_image=validated_data.get('profile_image'),# 任意のプロフィール画像を取得して渡す
            bio=validated_data.get('bio'),# 任意の自己紹介文
            prefecture=validated_data.get('prefecture'),# 任意の都道府県
        )
        return user# 作成したユーザーオブジェクトを返す

class UserChatRoomSerializer(serializers.ModelSerializer): # UserChatRoom モデルに対応したシリアライザーを定義
    class Meta:
        model = UserChatRoom# 対象となるモデルを指定
        fields = ['id']   # シリアライズ対象のフィールド（id のみ）を指定。必要に応じて追加可
        
class ChatMessageSerializer(serializers.ModelSerializer):# ChatMessage モデルに対応したシリアライザーを定義
    
    # sender（外部キー）から関連する username を取得して新しいフィールドとして追加
    # sender は CustomUser モデルへの外部キー。そこから username をたどって取得
    # 書き込み禁止。読み取り専用で、APIのレスポンスにのみ使われる
    sender_username = serializers.CharField(source='sender.username', read_only=True)  # 👈 これを追加！
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat_room', 'sender', 'sender_username', 'content', 'timestamp']