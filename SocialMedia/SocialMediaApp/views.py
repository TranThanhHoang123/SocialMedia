from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions
from .models import *
from django.db.models import Q
from rest_framework.response import Response
from . import serializers, utils, my_paginations
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from oauth2_provider.views import TokenView
from .utils import *
from oauth2_provider.models import Application, AccessToken, RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import AllowAny
from oauth2_provider.settings import oauth2_settings
import hashlib
import json
import uuid
from django.db import transaction
from .signals import *
import pdb



# Create your views here.

# Xu ly dang nhap bang refresh token http only
class CustomTokenView(TokenView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            data = json.loads(response.content)
            refresh_token = data.get('refresh_token')
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                expires=settings.OAUTH2_PROVIDER['REFRESH_TOKEN_EXPIRE_SECONDS'],
                secure=False,
                httponly=True,
                samesite='Lax'
            )
        return response


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_refresh_token(request):
    refresh_token = request.COOKIES.get('refresh_token')
    client_id = request.data.get('client_id')
    client_secret = request.data.get('client_secret')

    if not refresh_token:
        return JsonResponse({'error': 'No refresh token provided'}, status=400)

    if not client_id or not client_secret:
        return JsonResponse({'error': 'Client ID and client secret required'}, status=400)

    try:
        application = Application.objects.get(client_id=client_id)
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Invalid client credentials'}, status=400)

    # So sánh client_secret đã mã hóa
    if not check_client_secret(application.client_secret, client_secret):
        return JsonResponse({'error': 'Invalid client credentials'}, status=400)

    try:
        token = RefreshToken.objects.get(token=refresh_token, application=application)
    except RefreshToken.DoesNotExist:
        return JsonResponse({'error': 'Invalid refresh token'}, status=400)

        # Tính toán thời gian hết hạn của refresh token
        token_expires_at = token.updated + timedelta(seconds=OAUTH2_PROVIDER['REFRESH_TOKEN_EXPIRE_SECONDS'])

        # Kiểm tra thời gian hết hạn
        if timezone.now() > token_expires_at:
            return JsonResponse({'error': 'Refresh token expired'}, status=400)

    user = token.user

    # Tạo token ngẫu nhiên
    new_access_token = uuid.uuid4().hex

    # Lưu access token mới vào cơ sở dữ liệu
    new_access_token_obj = AccessToken.objects.create(
        user=user,
        application=application,
        token=new_access_token,
        expires=timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
    )

    response_data = {
        'access_token': new_access_token_obj.token,
        'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
    }

    return JsonResponse(response_data)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = my_paginations.UserPagination
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        return self.request.user

    @action(methods=['get', 'patch'], detail=False, url_path='profile')
    def profile(self, request, pk=None):
        user = self.get_object()
        if request.method == 'GET':
            return Response(serializers.UserDetailSerializer(user, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            profile = user.profile
            serializer = serializers.ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Sửa đổi Profile thành công'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='follow')
    def follow(self, request, pk=None):
        user = self.get_object()
        try:
            to_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if user == to_user:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        follow, created = Follow.objects.get_or_create(from_user=user, to_user=to_user)
        if not created:
            follow.delete()
            return Response({'message': 'Unfollowed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Followed successfully'}, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False, url_path='following')
    def following(self, request, pk=None):
        user = self.get_object()
        following_users = User.objects.filter(follower__from_user=user)
        page = self.paginate_queryset(following_users)
        serializer = serializers.UserListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['get'], detail=False, url_path='followers')
    def followers(self, request, pk=None):
        user = self.get_object()
        followers_users = User.objects.filter(following__to_user=user)
        page = self.paginate_queryset(followers_users)
        serializer = serializers.UserListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class PostViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.DestroyAPIView, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_date')
    serializer_class = serializers.PostSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = my_paginations.PostPagination

    def get_serializer_class(self):
        if self.action in ['list', 'get_personal_posts_list']:
            return serializers.PostDetailSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        comments = Comment.objects.filter(post=post, parent=None).order_by('-created_date')
        paginator = my_paginations.CommentPagination()
        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            comment_serializer = serializers.CommentListSerializer(page, many=True, context={'request': request})
            comments_data = paginator.get_paginated_response(comment_serializer.data).data
        else:
            comment_serializer = serializers.CommentListSerializer(comments, many=True, context={'request': request})
            comments_data = {
                'count': len(comments),
                'next': None,
                'previous': None,
                'results': comment_serializer.data
            }
        post_serializer = serializers.PostDetailSerializer(post, context={'request': request})
        response_data = {
            'post': post_serializer.data,
            'comments': comments_data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post', 'get'], detail=True, url_path='like')
    def like(self, request, pk=None):
        user = request.user
        post = get_object_or_404(Post, pk=pk)
        if request.method == 'POST':
            like, created = Like.objects.get_or_create(user=user, post=post)
            if created:
                return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'status': 'already liked'}, status=status.HTTP_200_OK)
        elif request.method == 'GET':
            likes = Like.objects.filter(post=post).select_related('user')
            users = [like.user for like in likes]
            page = self.paginate_queryset(users)
            if page is not None:
                serializer = serializers.UserDetailSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            serializer = serializers.UserDetailSerializer(users, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='unlike')
    def unlike(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        like = get_object_or_404(Like, user=request.user, post=post)
        like.delete()
        return Response({'status': 'unliked'}, status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        content = self.request.data.get('content')
        visibility = self.request.data.get('visibility')
        custom_viewers_ids = self.request.data.getlist('custom_viewers')
        media = self.request.FILES.getlist('media')
        post = Post.objects.create(user=user, content=content, visibility=visibility)
        if visibility == 'custom':
            custom_viewers = User.objects.filter(id__in=custom_viewers_ids)
            post.custom_viewers.set(custom_viewers)
        for file in media:
            Media.objects.create(post=post, file=file)
        return Response(serializers.PostDetailSerializer(post, context={'request': request}).data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user = request.user
        following = user.following.all().values_list('to_user', flat=True)
        queryset = Post.objects.filter(
            Q(visibility='public') |
            Q(user=user) |
            Q(visibility='followers', user__in=following) |
            Q(visibility='custom', custom_viewers=user)
        ).distinct().order_by('-created_date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Kiểm tra nếu DELETE được thực hiện từ endpoint không đúng
        if self.action != 'destroy':
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        disconnect_signals_decrease_like_count()
        post = get_object_or_404(Post, pk=kwargs['pk'], user=request.user)
        post.delete()
        return Response({'message': 'Xóa bài viết thành công'}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'get'], detail=True, url_path='comment')
    def comment(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        if request.method == 'POST':
            data = request.data.copy()
            data['user'] = request.user.id
            data['post'] = pk
            parent_id = data.get('parent')
            if parent_id:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
                data['parent'] = parent_comment.id
            serializer = serializers.CommentSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                comment = serializer.save()
                response_serializer = serializers.CommentListSerializer(comment, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'GET':
            comments = Comment.objects.filter(post=post, parent=None).order_by('-created_at')
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = serializers.CommentListSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            serializer = serializers.CommentListSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)

    def partial_update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk, user=request.user)
        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            updated_post = serializer.save()
            if 'visibility' in request.data and request.data['visibility'] != 'custom':
                updated_post.custom_viewers.clear()
            new_media = request.FILES.getlist('media')
            if new_media:
                for file in new_media:
                    Media.objects.create(post=updated_post, file=file)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='personal', detail=False)
    def get_personal_posts_list(self, request, pk=None):
        user = request.user
        posts = Post.objects.filter(user=user).order_by('-created_date')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = serializers.PostDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = serializers.PostDetailSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)



class CommentViewSet(viewsets.ViewSet,generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = my_paginations.CommentPagination

    @action(methods=['get'], detail=True, url_path='reply')
    def reply(self, request, pk=None):
        parent = get_object_or_404(Comment, pk=pk)
        # Lấy danh sách bình luận phản hồi với phân trang
        replies = Comment.objects.filter(parent=parent).order_by('-created_date')
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = serializers.CommentListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = serializers.CommentListSerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
    def update(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        old_file = comment.file
        serializer = self.serializer_class(comment, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_comment = serializer.save()
            if 'file' in request.FILES:
                if old_file:
                    old_file.delete(False)  # Xóa file cũ nếu có file mới được upload
                updated_comment.file = request.FILES['file']  # Gán file mới
                updated_comment.save()
            return Response(serializers.CommentListSerializer(updated_comment, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        comment.delete()  # Xóa comment và tệp tin đính kèm
        return Response({'message': 'Xóa thành công comment'}, status=status.HTTP_204_NO_CONTENT)