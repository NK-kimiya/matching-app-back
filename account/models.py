from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    prefecture = models.CharField(max_length=100, null=True, blank=True)
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("★ 使用中のストレージクラス:", self.profile_image.storage.__class__)
        print("★ アップロードされたファイル名:", self.profile_image.name)
        print("★ アップロードされた画像URL:", self.profile_image.url)

'''
誰が誰にマッチング申請したか
その申請が承認されたか
いつ申請したか
'''
class FriendRequest(models.Model):
    # 申請を送った側のユーザー（外部キーでCustomUserを参照）
    # related_name='sent_requests' により、user.sent_requests で送信済の申請一覧を取得できる
    from_user = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    
    #申請を受け取った側のユーザー（こちらもCustomUser）
    #user.received_requests で受信済みの申請一覧が取れるようになる
    to_user = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    
    #この申請が承認されたかどうかを示すフラグ（初期値はFalse＝未承認）
    is_accepted = models.BooleanField(default=False)
    
    # この申請が作られた日時を自動で記録
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # 同じ人に複数回申請できないように

'''
2人のユーザー間で1つのチャットルームを管理するモデル
フレンド同士になったら専用のチャットルームが作成される想定
'''
class ChatRoom(models.Model):
    #チャット相手の1人目
    #related_name='chatrooms1' により、user.chatrooms1 でアクセスできる
    user1 = models.ForeignKey(CustomUser, related_name='chatrooms1', on_delete=models.CASCADE)
    
    #チャット相手の2人目
    # related_name='chatrooms2' により、user.chatrooms2 でアクセス可能
    user2 = models.ForeignKey(CustomUser, related_name='chatrooms2', on_delete=models.CASCADE)
    
    #このチャットルームが作成された日時を自動記録
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        #同じ組み合わせの2人に対しては1つのチャットルームしか作れないように制限
        unique_together = ('user1', 'user2')