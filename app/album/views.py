"""
Views for the Albums API.
"""
from rest_framework import viewsets, authentication, permissions
from core.models import Album, Photo, User
from album.serializers import AlbumSerializer, PhotoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class AlbumViewSet(viewsets.ModelViewSet):
    """Manage Album in the database."""
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Create a new album."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Belirli bir albumun photos listele."""
        album = self.get_object()
        photos = album.photos.all()  # İlgili photos al
        return Response(PhotoSerializer(photos, many=True).data)

    @action(detail=True, methods=['get'], url_path='user_albums')
    def user_albums(self, request, pk=None):
        """Get all albums items for a specific user by user_id."""
        if not User.objects.filter(id=pk).exists():
            return Response(
                {"detail": "Belirtilen user_id'ye sahip bir kullanıcı bulunamadı."},
                status=404
            )
        albums = Album.objects.filter(user__id=pk)
        # Serileştirme işlemi
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)


class PhotoViewSet(viewsets.ModelViewSet):
    """Manage photos in the database."""
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapan kullanıcılar görebilir.

    def perform_create(self, serializer):
        """Create a new photo."""
        user = self.request.user  # Oturum açmış kullanıcıyı alıyoruz
        serializer.save(user=user)
