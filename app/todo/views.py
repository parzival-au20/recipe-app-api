"""
Views for the To-Do API.
"""
from rest_framework import viewsets, authentication, permissions
from core.models import ToDo, User
from todo.serializers import ToDoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class ToDoViewSet(viewsets.ModelViewSet):
    """Manage to-do in the database."""
    queryset = ToDo.objects.all()
    serializer_class = ToDoSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapan kullanıcılar görebilir.

    def perform_create(self, serializer):
        """Create a new to-do."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='user_todos')
    def user_todos(self, request, pk=None):
        """Get all to-do items for a specific user by user_id."""
        # Kullanıcının var olup olmadığını kontrol et
        if not User.objects.filter(id=pk).exists():
            return Response(
                {"detail": "Belirtilen user_id'ye sahip bir kullanıcı bulunamadı."},
                status=404
            )
        todos = ToDo.objects.filter(user__id=pk)
        # Serileştirme işlemi
        serializer = ToDoSerializer(todos, many=True)
        return Response(serializer.data)
