from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True,null=True)
    updated_date = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)

    class Meta:
        unique_together = ['email']


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    profile_background = models.ImageField(upload_to='user/%Y/%m', default='user/avatar.svg')
    profile_picture = models.ImageField(upload_to='user/%Y/%m', default='user/avatar.svg')
    public_profile = models.BooleanField(default=True)  # Trường để xác định trang cá nhân có công khai hay riêng tư


class Post(BaseModel):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('private', 'Only Me'),
        ('custom', 'Custom'),
    ]
    content = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=7, choices=VISIBILITY_CHOICES, default='public')
    custom_viewers = models.ManyToManyField(User, related_name='custom_view_posts', blank=True)

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
    file = models.FileField(upload_to='comment/%Y/%m', blank=True, null=True)  # Đính kèm video


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True,null=True)