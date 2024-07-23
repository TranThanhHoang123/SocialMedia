from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions
from .models import *
from django.db.models import Q
from rest_framework.response import Response
from . import serializers,utils,my_paginations
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
# Create your views here.


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_object(self):
        return self.request.user

    @action(methods=['get','patch'], detail=False, url_path='profile')
    def profile(self, request, pk=None):
        user = self.get_object()
        if request.method == 'GET':
            return Response(serializers.UserDetailSerializer(user,context={'request':request}).data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            profile = user.profile
            serializer = serializers.ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Sửa đổi Profile thành công'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = my_paginations.PostPagination  # Sử dụng phân trang tùy chỉnh

    @action(methods=['get'], url_path='comments', detail=True)  # Sửa 'pk=True' thành 'detail=True'
    def get_comment(self, request, pk=None):
        post = self.get_object()  # Lấy đối tượng Post dựa trên pk
        comments = Comment.objects.filter(post=post)  # Lọc các bình luận liên quan đến post

        # Phân trang bình luận
        paginator = my_paginations.CommentPagination()
        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = serializers.CommentListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        # Nếu không có phân trang, trả về tất cả bình luận
        serializer = serializers.CommentListSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        content = self.request.data.get('content')
        visibility = self.request.data.get('visibility')
        custom_viewers = self.request.data.get('custom_viewers',[])
        media = self.request.FILES.getlist('media')  # Lấy danh sách các file media
        post = Post.objects.create(user=user, content=content, visibility=visibility)
        if visibility == 'custom':
            post.custom_viewers.set(custom_viewers)

        for file in media:
            Media.objects.create(post=post, file=file)
        return Response(serializers.PostDetailSerializer(post, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user = request.user
        friends = user.friends.all()  # Giả định rằng bạn có một mối quan hệ nhiều-nhiều giữa người dùng và bạn bè

        queryset = Post.objects.filter(
            Q(visibility='public') |
            Q(user=user) |
            Q(visibility='friends', user__in=friends) |
            Q(visibility='custom', custom_viewers=user)
        ).distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.PostDetailSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.PostDetailSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk, user=request.user)
        post.delete()
        return Response({'message': 'Xóa bài viết thành công'}, status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ViewSet):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = my_paginations.CommentPagination

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save()
            response_serializer = serializers.CommentListSerializer(comment, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'message': 'Xóa thành công comment'},status=status.HTTP_204_NO_CONTENT)
