# Generated by Django 5.0.2 on 2024-03-01 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='profile',
        ),
    ]
