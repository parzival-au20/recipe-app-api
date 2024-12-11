"""
Serializers for the posts API View
"""

from core.models import Post, Comment
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    """ Serializer for the post object."""
    # comments = serializers.StringRelatedField(many=True, read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model = Post
        fields = ['userId', 'id', 'title', 'body']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the comment object."""
    name = serializers.CharField(source='user.name', read_only=True)  # Kullanıcı adı otomatik alınacak
    email = serializers.EmailField(source='user.email', read_only=True)  # Kullanıcı e-postası otomatik alınacak

    class Meta:
        model = Comment
        fields = ['postId', 'id', 'name', 'email', 'body']
