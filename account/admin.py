from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FriendRequest, ChatRoom

# CustomUserモデルの管理画面設定
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # 管理画面で表示するフィールド
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'prefecture', 'date_joined', 'is_active')
    
    # 検索可能なフィールド
    search_fields = ('username', 'email', 'first_name', 'last_name', 'prefecture')
    
    # フィルター可能なフィールド
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'prefecture')
    
    # 1ページあたりの表示件数
    list_per_page = 20
    
    # 編集画面で表示するフィールドセット
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('個人情報', {'fields': ('first_name', 'last_name', 'email', 'profile_image', 'bio', 'prefecture')}),
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('フレンド関係', {'fields': ('friends',)}),
        ('重要な日付', {'fields': ('last_login', 'date_joined')}),
    )
    
    # 新規作成時のフィールド
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'prefecture'),
        }),
    )
    
    # 読み取り専用フィールド
    readonly_fields = ('date_joined', 'last_login')

# FriendRequestモデルの管理画面設定
@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    # 管理画面で表示するフィールド
    list_display = ('id', 'from_user', 'to_user', 'is_accepted', 'timestamp')
    
    # 検索可能なフィールド
    search_fields = ('from_user__username', 'to_user__username', 'from_user__email', 'to_user__email')
    
    # フィルター可能なフィールド
    list_filter = ('is_accepted', 'timestamp')
    
    # 1ページあたりの表示件数
    list_per_page = 20
    
    # 編集画面で表示するフィールド
    fields = ('from_user', 'to_user', 'is_accepted', 'timestamp')
    
    # 読み取り専用フィールド
    readonly_fields = ('timestamp',)
    
    # 日付でソート（新しい順）
    ordering = ('-timestamp',)
    
    # 一括操作
    actions = ['accept_requests', 'reject_requests']
    
    def accept_requests(self, request, queryset):
        """選択された申請を一括承認"""
        updated = queryset.update(is_accepted=True)
        self.message_user(request, f'{updated}件の申請を承認しました。')
    accept_requests.short_description = "選択された申請を承認"
    
    def reject_requests(self, request, queryset):
        """選択された申請を一括削除（拒否）"""
        deleted, _ = queryset.delete()
        self.message_user(request, f'{deleted}件の申請を削除しました。')
    reject_requests.short_description = "選択された申請を削除（拒否）"

# ChatRoomモデルの管理画面設定
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    # 管理画面で表示するフィールド
    list_display = ('id', 'user1', 'user2', 'created_at', 'get_participants')
    
    # 検索可能なフィールド
    search_fields = ('user1__username', 'user2__username', 'user1__email', 'user2__email')
    
    # フィルター可能なフィールド
    list_filter = ('created_at',)
    
    # 1ページあたりの表示件数
    list_per_page = 20
    
    # 編集画面で表示するフィールド
    fields = ('user1', 'user2', 'created_at')
    
    # 読み取り専用フィールド
    readonly_fields = ('created_at',)
    
    # 日付でソート（新しい順）
    ordering = ('-created_at',)
    
    def get_participants(self, obj):
        """参加者を表示するカスタムフィールド"""
        return f"{obj.user1.username} & {obj.user2.username}"
    get_participants.short_description = "参加者"
    
    # 一括操作
    actions = ['delete_old_rooms']
    
    def delete_old_rooms(self, request, queryset):
        """古いチャットルームを一括削除"""
        deleted, _ = queryset.delete()
        self.message_user(request, f'{deleted}件のチャットルームを削除しました。')
    delete_old_rooms.short_description = "選択されたチャットルームを削除"

# 管理画面のタイトルとヘッダーをカスタマイズ
admin.site.site_header = "マッチングアプリケーション管理画面"
admin.site.site_title = "マッチングアプリ管理"
admin.site.index_title = "管理画面へようこそ"
