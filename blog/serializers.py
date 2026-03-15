from rest_framework import serializers
from .models import Post, Category, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model  = Comment
        fields = ['id', 'author', 'content', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author   = serializers.StringRelatedField()
    category = CategorySerializer()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model  = Post
        fields = [
            'id', 'title', 'content', 'author',
            'category', 'image', 'status',
            'created_at', 'updated_at', 'comments'
        ]