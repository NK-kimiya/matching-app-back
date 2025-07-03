from django.urls import path
from .views import RegisterView,MeView,UserDetailByIdView,UserProfileUpdateView,UserListView,ChatRoomView,FriendRequestView,FriendRequestAcceptView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserDetailByIdView.as_view(), name='user-detail-by-id'),
    # チャットルームの一覧取得・作成
    path("chatrooms/", ChatRoomView.as_view(), name="chatroom"),
    # フレンド申請の送信・取得
    path("friend-requests/", FriendRequestView.as_view(), name="friend-request"),
    # フレンド申請の承認（POST: /friend-requests/3/accept/）
    path("friend-requests/<int:request_id>/accept/", FriendRequestAcceptView.as_view(), name="friend-request-accept"),
    
]