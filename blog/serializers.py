from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from blog.models import Profile, Post, Comment, Reply, FavoritePost, CustomUser, Follower, Like


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=15)
    password = serializers.CharField(max_length=15)


class ProfileSerializer(ModelSerializer):
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id','first_name','last_name', 'bio', 'avatar', 'date_of_birth', 'user', 'follower_count')

    def get_follower_count(self, obj):
        return Follower.objects.filter(following=obj.user).count()


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'
class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content',  'user', 'created_at']


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class ReplySerializer(ModelSerializer):
    class Meta:
        model = Reply
        fields = "__all__"


class FavouritePostSerializer(ModelSerializer):
    class Meta:
        model = FavoritePost
        fields = "__all__"


class CustomRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=250)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'object_id', 'created_at']