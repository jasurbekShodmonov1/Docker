from linecache import cache
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate
from django.http import Http404
from drf_yasg import openapi
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Profile, Post, Comment, Reply, FavoritePost, Follower, Like
from .serializers import UserSerializer, ProfileSerializer, PostSerializer, CommentSerializer, ReplySerializer, \
    FavouritePostSerializer, CustomRefreshSerializer, CustomLoginSerializer, FollowerSerializer, LikeSerializer

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, filters
from rest_framework.decorators import permission_classes, api_view, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


@swagger_auto_schema(
    method='post',
    request_body=CustomLoginSerializer,
    responses={200: 'Success'},
    examples={
        'application/json': {
            'username': 'username1',
            'password': 'random_password123$',
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def post_login(request, *args, **kwargs):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({"access_token": access_token,
                         "refresh_token": refresh_token,
                         "user_role": user.user_role}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method='post',
    request_body=CustomRefreshSerializer,
    responses={200: 'Success'},
    examples={
        'application/json': {
            'refresh_token': 'fdgdfasd',
        }
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request, *args, **kwargs):
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the refresh token is valid
    try:
        # Parse the provided refresh token
        refresh_token = RefreshToken(refresh_token)
        refresh_token.verify()
    except TokenError as e:
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

    # Get user ID from the refresh token
    user_id = refresh_token.payload.get('user_id')

    try:
        # Get the user object based on the user ID
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        raise Http404("User does not exist")

    # Blacklist the current access and refresh tokens
    blacklist_access_token(refresh_token.access_token)
    blacklist_refresh_token(refresh_token)

    # Generate new tokens for the user
    new_tokens = generate_tokens_for_user(user)

    return Response(new_tokens, status=status.HTTP_200_OK)

def blacklist_access_token(access_token):
    # Blacklist the current access token
    cache_key = f"blacklist_{access_token}"
    cache.set(cache_key, "blacklisted", timeout=access_token.lifetime.total_seconds())

def blacklist_refresh_token(refresh_token):
    # Blacklist the current refresh token
    user_id = refresh_token.payload.get('user_id')
    cache_key = f"blacklist_{user_id}_refresh"
    old_refresh_token = str(refresh_token)
    cache.set(cache_key, old_refresh_token, timeout=refresh_token.lifetime.total_seconds())

def generate_tokens_for_user(user):
    # Generate new tokens for the user
    new_refresh = RefreshToken.for_user(user)
    new_access_token = str(new_refresh.access_token)
    new_refresh_token = str(new_refresh)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }



class ProfileFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')

    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name']  # Add other valid model fields here if needed


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfileFilter
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        user_profile = self.get_object()
        likes = Like.objects.filter(user=user_profile.user)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_profile(self, request, pk=None):
        user_profile = self.get_object()

        # Delete associated user
        user_profile.user.delete()

        # Delete user profile
        user_profile.delete()

        return Response({'detail': 'User profile and associated user deleted successfully.'},
                        status=status.HTTP_204_NO_CONTENT)

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        follower = self.request.user
        following = self.get_object().user

        if Follower.objects.filter(follower=follower, following=following).exists():
            return Response({'detail': 'Already following'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'follower': follower.id, 'following': following.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': 'Followed successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        follower = self.request.user
        following = self.get_object().user

        try:
            instance = Follower.objects.get(follower=follower, following=following)
            instance.delete()
            return Response({'detail': 'Unfollowed successfully'}, status=status.HTTP_200_OK)
        except Follower.DoesNotExist:
            return Response({'detail': 'Not following'}, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]


class CommmentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, content_type='comment', object_id=comment.id)
        return Response({'liked': created})


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]


class FavouritePostViewSet(viewsets.ModelViewSet):
    queryset = FavoritePost.objects.all()
    serializer_class = FavouritePostSerializer
    permission_classes = [IsAuthenticated]