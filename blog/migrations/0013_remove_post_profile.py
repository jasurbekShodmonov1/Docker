# Generated by Django 5.0.2 on 2024-03-03 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_alter_customuser_groups_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='profile',
        ),
    ]