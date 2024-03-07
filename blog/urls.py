from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet, ProfileViewSet, PostViewSet, CommmentViewSet, ReplyViewSet,FavouritePostViewSet, FollowerViewSet, LikeViewSet


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'followers', FollowerViewSet, basename='followers')
router.register(r'post', PostViewSet, basename='post')
router.register(r'comment', CommmentViewSet, basename='comment')
router.register(r'reply', ReplyViewSet, basename='reply')
router.register(r'favouritePost', FavouritePostViewSet, basename='favouritePost')
router.register(r'likes', LikeViewSet, basename='likes')


urlpatterns = [
    path('', include(router.urls)),
    ]

