# Generated by Django 5.0.7 on 2024-07-18 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialMediaApp', '0005_emailconfirm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(default='https://api.dicebear.com/8.x/lorelei-neutral/svg?seed=John', upload_to='user/%Y/%m'),
        ),
    ]
