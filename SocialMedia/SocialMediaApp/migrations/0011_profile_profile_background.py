# Generated by Django 5.0.7 on 2024-07-18 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMediaApp', '0010_remove_user_confirmation_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_background',
            field=models.ImageField(default='user/avatar.svg', upload_to='user/%Y/%m'),
        ),
    ]
