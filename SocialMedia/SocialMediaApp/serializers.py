from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password','last_name','first_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(data['password'])
        user.save()
        Profile.objects.create(user=user)
        return user


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'

class ProfileDetailSerializer(ProfileSerializer):
    profile_background = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            # Lấy tên file hình ảnh từ đường dẫn được lưu trong trường image
            profile_picture = obj.profile_picture.name
            return self.context['request'].build_absolute_uri(f"/static/{profile_picture}")

    def get_profile_background(self, obj):
        if obj.profile_background:
            # Lấy tên file hình ảnh từ đường dẫn được lưu trong trường image
            profile_background = obj.profile_background.name
            return self.context['request'].build_absolute_uri(f"/static/{profile_background}")
        return None
    class Meta(ProfileSerializer.Meta):
        pass


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file']


class PostSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['id', 'content', 'media']

    def create(self,validated_data):
        user = self.context['request'].user
        media_data = validated_data.pop('media', [])
        post = Post.objects.create(user=user, **validated_data)
        for media_item in media_data:
            Media.objects.create(post=post, **media_item)
        return post


class PostDetailSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        pass


