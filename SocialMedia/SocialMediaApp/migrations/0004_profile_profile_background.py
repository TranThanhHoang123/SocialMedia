# Generated by Django 5.0.7 on 2024-07-18 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMediaApp', '0003_profile_public_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_background',
            field=models.ImageField(blank=True, null=True, upload_to='user/%Y/%m'),
        ),
    ]
