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
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        if obj.file:
            # Lấy tên file hình ảnh từ đường dẫn được lưu trong trường image
            file = obj.file.name
            return self.context['request'].build_absolute_uri(f"/static/{file}")
    class Meta:
        model = Media
        fields = ['id', 'file']


class PostSerializer(serializers.ModelSerializer):
    media = MediaSerializer(many=True, required=False)
    custom_viewers = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    class Meta:
        model = Post
        fields = ['id', 'content', 'media','visibility','custom_viewers']

#profile hiển thị theo post
class ProfilePostSerializer(serializers.ModelSerializer):
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
        fields = ['profile_picture','profile_background']


#user hiển thị theo post
class UserPostSerializer(serializers.ModelSerializer):
    profile = ProfilePostSerializer()
    class Meta:
        model = User
        fields = ['first_name', 'last_name','profile']

class PostDetailSerializer(PostSerializer):
    user = UserPostSerializer()
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['user']


#comment vào post
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'file']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentListSerializer(CommentSerializer):
    user = UserPostSerializer()
    file = serializers.SerializerMethodField()
    def get_file(self, obj):
        if obj.file:
            # Lấy tên file hình ảnh từ đường dẫn được lưu trong trường image
            file = obj.file.name
            return self.context['request'].build_absolute_uri(f"/static/{file}")
    class Meta(CommentSerializer.Meta):
        pass


