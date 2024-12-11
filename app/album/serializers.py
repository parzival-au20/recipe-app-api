"""
Serializers for the album API View
"""
from django.contrib.auth import  authenticate

from django.utils.translation import gettext as _
from core.models import Album, Photo, User

from rest_framework import serializers


class AlbumSerializer(serializers.ModelSerializer):
    """ Serializer for the album object."""
    #photos = serializers.StringRelatedField(many=True, read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model = Album
        fields = ['userId','id', 'title']



class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for the photo object."""

    class Meta:
        model = Photo
        fields = ['albumId', 'id', 'title', 'url', 'thumbnailUrl']