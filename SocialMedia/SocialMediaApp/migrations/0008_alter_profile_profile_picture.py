# Generated by Django 5.0.7 on 2024-07-18 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMediaApp', '0007_remove_profile_profile_background'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(default='user/avatar.svg', upload_to='user/%Y/%m'),
        ),
    ]
