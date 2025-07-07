from django.urls import path
from .views import RegisterView,MeView,UserDetailByIdView,UserProfileUpdateView,UserListView,ChatMessageCreateView,ChatMessageListView,ChatRoomParticipantsView
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
    path('chat/messages/', ChatMessageCreateView.as_view(), name='chat-message-create'),
    path('chat/messages/<int:chat_room_id>/', ChatMessageListView.as_view(), name='chat-message-list'),
    path('chat/participants/', ChatRoomParticipantsView.as_view(), name='chat-participants'),
]