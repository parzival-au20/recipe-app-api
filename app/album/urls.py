"""
URL mappings for Album API
"""


from rest_framework.routers import DefaultRouter
from album.views import AlbumViewSet, PhotoViewSet

app_name = 'album'


router = DefaultRouter()
router.register('albums', AlbumViewSet)
router.register('photos', PhotoViewSet)

urlpatterns = [
    # Diğer URL'ler
] + router.urls