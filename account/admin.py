from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,UserChatRoom

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

@admin.register(UserChatRoom)
class UserChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')       # 一覧に表示する項目
    search_fields = ('user__username',) # ユーザー名で検索

# FriendRequestモデルの管理画面設定
# 管理画面のタイトルとヘッダーをカスタマイズ
admin.site.site_header = "マッチングアプリケーション管理画面"
admin.site.site_title = "マッチングアプリ管理"
admin.site.index_title = "管理画面へようこそ"
