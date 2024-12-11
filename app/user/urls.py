"""
URL mappings for user API
"""
# user/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, CreateTokenView

app_name = 'user'

# Router'ı oluştur
router = DefaultRouter()

# UserViewSet'i router'a ekle
router.register('users', UserViewSet)


urlpatterns = [
    path('token/', CreateTokenView.as_view(), name='token'),
] + router.urls
