"""
Views for the user API.
"""
from rest_framework import viewsets, authentication, permissions
from core.models import User
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

class UserViewSet(viewsets.ModelViewSet):
    """Manage users in the system."""
    serializer_class = UserSerializer
    queryset = User.objects.all()  # Tüm kullanıcıları sorgula
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Override perform_create to handle user creation"""
        serializer.save()
    def get_permissions(self):
        """
        Override get_permissions to handle authentication only on non-create operations.
        """
        if self.action == 'create':
            # POST işlemi (create) için kimlik doğrulama gerekmiyor
            return []  # Kimlik doğrulaması gerekmiyor
        # Diğer CRUD işlemleri için token doğrulaması yapılacak.
        return [permission() for permission in self.permission_classes]

    # CRUD işlemleri otomatik olarak sağlanır (create, update, retrieve, delete).

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    # Token oluşturma işlemi için özel bir view kullanmaya devam ediyoruz.
