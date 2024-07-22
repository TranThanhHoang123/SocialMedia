from django.shortcuts import render
from rest_framework import viewsets, generics, status, permissions
from .models import *
from rest_framework.response import Response
from . import serializers,utils
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return self.permission_classes

    def get_object(self):
        return self.request.user

    @action(methods=['get','patch'], detail=False, url_path='profile')
    def profile(self, request, pk=None):
        user = self.get_object()
        if request.method == 'GET':
            return Response(serializers.ProfileDetailSerializer(user.profile,context={'request':request}).data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            profile = user.profile
            serializer = serializers.ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Sửa đổi Profile thành công'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ViewSet,generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # Gọi phương thức create của serializer để lưu bài đăng và các media liên quan
        serializer.save()

