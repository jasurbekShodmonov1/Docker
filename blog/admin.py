from django.contrib import admin

from blog.models import CustomUser, Profile, Post, Comment, Reply, FavoritePost

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(FavoritePost)