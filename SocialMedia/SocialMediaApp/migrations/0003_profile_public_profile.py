# Generated by Django 5.0.7 on 2024-07-18 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMediaApp', '0002_remove_profile_active_remove_user_created_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='public_profile',
            field=models.BooleanField(default=True),
        ),
    ]
