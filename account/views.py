# type: ignore
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,CustomUserSerializer
from rest_framework import generics,permissions
from .models import CustomUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView
from django.db.models import Q
from django.shortcuts import get_object_or_404

'''
ユーザーの作成
'''
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'ユーザー登録成功'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 認証済ユーザーのみアクセス可能

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

'''
Userのアップデート
'''
class UserProfileUpdateView(APIView):
    # 認証されているユーザーのみがこのビューにアクセスできるようにする
    permission_classes = [permissions.IsAuthenticated]
    # フロントエンドから画像（profile_image）などのファイルを受け取るために、パーサを設定
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        # 現在ログインしているユーザー（request.user）を対象に、
        # フロントエンドから送られたデータ（request.data）で部分更新を試みる
        serializer = CustomUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid(): # データのバリデーション（入力チェック）が正しければ
            serializer.save()# ユーザー情報を保存（更新）する
            return Response({'message': '更新に成功しました'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

'''
全ユーザー取得のビュー
'''

class UserListView(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]  # 認証済みのユーザーのみアクセス可能

'''
個別ユーザー詳細取得のビュー
'''
class UserDetailByIdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)


