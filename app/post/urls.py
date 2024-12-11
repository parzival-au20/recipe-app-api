"""
URL mappings for post API
"""


from rest_framework.routers import DefaultRouter
from post.views import PostViewSet, CommentViewSet

app_name = 'post'


router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('comments', CommentViewSet)

urlpatterns = [
    # Diğer URL'ler
] + router.urls