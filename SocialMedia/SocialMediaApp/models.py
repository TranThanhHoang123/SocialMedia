from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True,null=True)
    updated_date = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    # Trường đếm số người đang theo dõi
    following_count = models.PositiveIntegerField(default=0)
    # Trường đếm số người theo dõi mình
    followers_count = models.PositiveIntegerField(default=0)


class Follow(models.Model):
    from_user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)  # Thay đổi related_name
    to_user = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)  # Thay đổi related_name
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_follow')
        ]

    def __str__(self):
        return f"{self.from_user} follows {self.to_user}"


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    profile_background = models.ImageField(upload_to='user/%Y/%m', default='user/avatar.svg')
    profile_picture = models.ImageField(upload_to='user/%Y/%m', default='user/avatar.svg')
    public_profile = models.BooleanField(default=True)  # Trường để xác định trang cá nhân có công khai hay riêng tư
    like_number = models.PositiveIntegerField(default=0)
    post_number = models.PositiveIntegerField(default=0)

class Post(BaseModel):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('followers', 'Follower'),
        ('private', 'Only Me'),
        ('custom', 'Custom'),
    ]
    like_number = models.PositiveIntegerField(default=0)
    comment_number = models.PositiveIntegerField(default=0)
    content = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=9, choices=VISIBILITY_CHOICES, default='public')
    custom_viewers = models.ManyToManyField(User, related_name='custom_view_posts', blank=True)

    def can_view(self, user):
        if self.visibility == 'public':
            return True
        if self.visibility == 'private' and self.user == user:
            return True
        if self.visibility == 'followers' and user in self.user.followers.all():
            return True
        if self.visibility == 'custom' and user in self.custom_viewers.all():
            return True
        return False

    def __str__(self):
        return f"Post {self.id}"


class Media(models.Model):
    post = models.ForeignKey(Post, related_name='media', on_delete=models.CASCADE)  # Mối quan hệ nhiều một với bài đăng
    file = models.FileField(upload_to='post/%Y/%m')  # Tệp tin đa phương tiện (video hoặc ảnh)

    def __str__(self):
        return f"Media {self.id} of Post {self.post.id}"


class Comment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='comment/%Y/%m', blank=True, null=True)  # Đính kèm video hoặc ảnh


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True,null=True)