from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *
from django.db.models import F
from django.db import transaction
from django.apps import apps

#signals
@receiver(post_delete, sender=Media)
def delete_media_file(sender, instance, **kwargs):
    instance.file.delete(False)


@receiver(post_delete, sender=Comment)
def delete_comment_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(False)


@receiver(post_save, sender=Like)
def increase_like_count(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            post = instance.post
            post.like_number = F('like_number') + 1
            post.save(update_fields=['like_number'])

            profile = post.user.profile
            profile.like_number = F('like_number') + 1
            profile.save()
            print('increase_like_count')

@receiver(post_delete, sender=Like)
def decrease_like_count(sender, instance, **kwargs):
    with transaction.atomic():
        post = instance.post
        post.like_number = F('like_number') - 1
        post.save(update_fields=['like_number'])

        profile = post.user.profile
        profile.like_number = F('like_number') - 1
        profile.save()
        print('decrease_like_count')


@receiver(post_save, sender=Comment)
def increase_comment_count(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.comment_number = F('comment_number') + 1
        post.save(update_fields=['comment_number'])
        print('increase_comment_count')


@receiver(post_delete, sender=Comment)
def decrease_comment_count(sender, instance, **kwargs):
    post = instance.post
    post.comment_number = F('comment_number') - 1
    post.save(update_fields=['comment_number'])
    print('decrease_comment_count')


@receiver(post_save, sender=Follow)
def update_follow_counts_on_create(sender, instance, created, **kwargs):
    if created:
        # Khi tạo một mối quan hệ theo dõi
        instance.from_user.following_count += 1
        instance.to_user.followers_count += 1
        instance.from_user.save()
        instance.to_user.save()
        print('update_follow_counts_on_create')

@receiver(post_delete, sender=Follow)
def update_follow_counts_on_delete(sender, instance, **kwargs):
    # Khi xóa một mối quan hệ theo dõi
    instance.from_user.following_count -= 1
    instance.to_user.followers_count -= 1
    instance.from_user.save()
    instance.to_user.save()
    print('update_follow_counts_on_delete')


@receiver(post_save, sender=Post)
def update_post_number_on_create(sender, instance, created, **kwargs):
    if created:
        # Khi một bài viết được tạo
        profile = instance.user.profile
        profile.post_number += 1
        profile.save()
        print('update_post_number_on_create')

@receiver(post_delete, sender=Post)
def update_profile_on_post_delete(sender, instance, **kwargs):
    # Sử dụng transaction.atomic() để đảm bảo tính nhất quán
    with transaction.atomic():
        profile = instance.user.profile
        # Lấy số lượt thích của bài viết bị xóa
        likes_count = instance.like_number
        # Cập nhật số lượt thích và số lượng bài viết trong profile
        profile.like_number = F('like_number') - likes_count
        profile.post_number = F('post_number') - 1
        profile.save()

def connect_signals():
    from .signals import (delete_media_file, delete_comment_file, increase_like_count,
                          decrease_like_count, increase_comment_count, decrease_comment_count,
                          update_follow_counts_on_create, update_follow_counts_on_delete,
                          update_post_number_on_create, update_profile_on_post_delete)

    models_and_signals = [
        (delete_media_file, 'SocialMediaApp.Media'),
        (delete_comment_file, 'SocialMediaApp.Comment'),
        (increase_like_count, 'SocialMediaApp.Like'),
        (decrease_like_count, 'SocialMediaApp.Like'),
        (increase_comment_count, 'SocialMediaApp.Comment'),
        (decrease_comment_count, 'SocialMediaApp.Comment'),
        (update_follow_counts_on_create, 'SocialMediaApp.Follow'),
        (update_follow_counts_on_delete, 'SocialMediaApp.Follow'),
        (update_post_number_on_create, 'SocialMediaApp.Post'),
        (update_profile_on_post_delete, 'SocialMediaApp.Post')
    ]

    for signal, sender in models_and_signals:
        model = apps.get_model(sender)
        post_save.connect(signal, sender=model)
        post_delete.connect(signal, sender=model)
def disconnect_signals_decrease_like_count():
    from .signals import decrease_like_count
    model = apps.get_model('SocialMediaApp.Like')
    post_delete.disconnect(decrease_like_count, sender=model)
