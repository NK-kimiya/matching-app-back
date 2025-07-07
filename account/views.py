# type: ignore
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,CustomUserSerializer,ChatMessageSerializer
from rest_framework import generics,permissions
from .models import CustomUser,ChatMessage,UserRoomParticipation,UserChatRoom
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


class ChatMessageCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()# リクエストデータを変更できるようにコピー
        data['sender'] = request.user.id# 現在ログイン中のユーザーのIDを sender フィールドに追加
        
         # 先にチャットルーム取得（Validation前に必要なため）
        chat_room_id = data.get('chat_room')# フロントから送られてきたチャットルームのIDを取得
        chat_room = get_object_or_404(UserChatRoom, id=chat_room_id)# IDに対応するチャットルームがなければ404を返す

        # 参加履歴の追加（重複は避ける）
        UserRoomParticipation.objects.get_or_create( # ユーザーとチャットルームのペアが存在しない場合のみ新たに作成
            user=request.user,# ログイン中のユーザー
            chat_room=chat_room # 取得したチャットルーム
        )

        serializer = ChatMessageSerializer(data=data)# メッセージデータをシリアライザーに渡してバリデーション準備
        if serializer.is_valid():# バリデーションOKなら
            serializer.save()# メッセージをDBに保存
            return Response(serializer.data, status=status.HTTP_201_CREATED)# 成功レスポンスを返す
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)# バリデーションエラーの場合は400を返す
    
class ChatMessageListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, chat_room_id):
        messages = ChatMessage.objects.filter(chat_room__id=chat_room_id).order_by('timestamp')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomParticipantsView(APIView):
    permission_classes = [permissions.IsAuthenticated]# 認証済みユーザーのみアクセスを許可

    def get(self, request):
        participations = UserRoomParticipation.objects.filter(user=request.user)
         # └ ① リクエストユーザー(request.user)に紐づく参加レコードを取得

        partners = [p.chat_room.user for p in participations]
         # └ ② 取得した各参加レコード(p)から、その chat_room に紐づくユーザー(CustomUser)を取り出してリスト化

        serializer = CustomUserSerializer(partners, many=True, context={'request': request})
        # └ ③ CustomUserSerializer を使って、ユーザーオブジェクトのリストをシリアライズ
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        # └ ④ シリアライズ済みデータを HTTP 200 OK としてクライアントに返却
