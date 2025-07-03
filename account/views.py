# type: ignore
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,CustomUserSerializer,ChatRoomSerializer,FriendRequestSerializer
from rest_framework import generics,permissions
from .models import CustomUser,ChatRoom,FriendRequest
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


'''
チャットルームの一覧取得・作成
'''
class ChatRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 自分が関係するチャットルームを取得
        user = request.user
        chatrooms = ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return Response(serializer.data)
    
    '''
    HTTP POSTリクエストでチャットルームを新規作成するAPIメソッド
    '''
    def post(self, request):
        #現在ログインしているユーザー（申請を出す側）を取得
        user = request.user
        # リクエストのデータ（POSTのbody）からチャット相手のユーザーIDを取得
        target_id = request.data.get("target_user_id")
        try:
            # 指定されたIDのユーザーが存在すれば取得
            target_user = CustomUser.objects.get(id=target_id)
        except CustomUser.DoesNotExist:
            # ユーザーが存在しない場合はエラーレスポンスを返す
            return Response({"error": "相手ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)

        #フレンドになっているかの確認
        if not target_user in user.friends.all():  # type: ignore
            return Response({"error": "まだフレンドではありません"}, status=status.HTTP_403_FORBIDDEN)

         # user1のIDが小さいように順番を固定（unique_together対策）
        user1, user2 = sorted([user, target_user], key=lambda u: u.id)  # type: ignore

        # すでに同じ2人のチャットルームが存在する場合は、新規作成せずメッセージを返す
        if ChatRoom.objects.filter(user1=user1, user2=user2).exists():
            return Response({"message": "すでにチャットルームが存在します"}, status=status.HTTP_200_OK)

        # チャットルームをデータベースに新規作成
        room = ChatRoom.objects.create(user1=user1, user2=user2)
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


'''
フレンド申請の送信・取得ビュー
このクラスは2つの機能を提供します：
1. POST: フレンド申請を送信する
2. GET: 自分宛のフレンド申請一覧を取得する
'''
class FriendRequestView(APIView):
    # 認証済みユーザーのみがアクセス可能
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        POST /api/friend-requests/
        フレンド申請を送信するメソッド
        
        リクエストボディ例:
        {
            "to_user_id": 123
        }
        """
        # リクエストボディから申請先ユーザーのIDを取得
        to_user_id = request.data.get("to_user_id")
        
        # 指定されたIDのユーザーが存在するかチェック
        # 存在しない場合は404エラーを自動で返す
        to_user = get_object_or_404(CustomUser, id=to_user_id)

        # 既に同じユーザーに申請を送信済みかチェック
        # from_user=request.user（自分）からto_user（相手）への申請が存在するか確認
        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
            return Response({"message": "すでに申請済みです"}, status=400)

        # 自分自身に申請を送信しようとしていないかチェック
        if request.user == to_user:
            return Response({"message": "自分には申請できません"}, status=400)

        # フレンド申請をデータベースに作成
        # from_user: 申請を送る側（自分）
        # to_user: 申請を受け取る側（相手）
        friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
        
        # 作成された申請データをシリアライズしてレスポンス
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=201)

    def get(self, request):
        """
        GET /api/friend-requests/
        自分宛のフレンド申請一覧を取得するメソッド
        
        レスポンス例:
        [
            {
                "id": 1,
                "from_user": 123,
                "to_user": 456,
                "is_accepted": false,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ]
        """
        # 自分（request.user）宛の未承認申請のみを取得
        # to_user=request.user: 自分が申請を受け取る側
        # is_accepted=False: まだ承認されていない申請のみ
        requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)
        
        # 複数の申請データをシリアライズ（many=True）
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    
'''
フレンド申請の承認ビュー
POST: /api/friend-requests/{request_id}/accept/
特定のフレンド申請を承認し、フレンド関係を確立する
'''
class FriendRequestAcceptView(APIView):
    # 認証済みユーザーのみがアクセス可能
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        """
        POST /api/friend-requests/{request_id}/accept/
        フレンド申請を承認するメソッド
        
        パラメータ:
        - request_id: 承認するフレンド申請のID
        
        処理の流れ:
        1. 申請が存在するかチェック
        2. 自分宛の申請かチェック
        3. 既に承認済みかチェック
        4. 申請を承認状態に更新
        5. フレンド関係を両者に追加
        """
        # フレンド申請（FriendRequest）モデルから該当する申請IDのデータを取得
        # もし存在しなければ 404 エラーを自動で返す
        friend_request = get_object_or_404(FriendRequest, id=request_id)

        # ログインユーザーが、この申請の「申請された側（to_user）」か確認
        # 自分宛の申請でない場合は403エラー（権限なし）
        if friend_request.to_user != request.user:
            return Response({"error": "あなたに届いた申請ではありません"}, status=403)

        # すでに承認済みなら、二重処理を避けて「承認済みです」と返す
        # 同じ申請を複数回承認することを防ぐ
        if friend_request.is_accepted:
            return Response({"message": "すでに承認されています"}, status=200)

        # フレンド申請を承認状態にして保存（DB更新）
        # is_acceptedをTrueに変更してデータベースに保存
        friend_request.is_accepted = True
        friend_request.save()

        # フレンド関係を追加（両者に追加）
        # CustomUserモデルのManyToManyField(friends)に互いを追加する
        # これにより、両者がフレンドとして認識されるようになる
        friend_request.from_user.friends.add(friend_request.to_user)  # 申請者に相手を追加
        friend_request.to_user.friends.add(friend_request.from_user)  # 相手に申請者を追加

        # 承認完了のメッセージを返す
        return Response({"message": "フレンド申請を承認しました"}, status=200)