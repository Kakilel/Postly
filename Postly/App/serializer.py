from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Category, Comment, Like

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "body", "created_at"]


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "timestamp"]


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = serializers.StringRelatedField()
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, source="like_set", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "author", "category", "content", "image",
            "created_at", "updated_at", "published_date", "featured",
            "total_likes", "comments", "likes"
        ]


class CategorySerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "posts"]
