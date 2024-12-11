"""
Views for the Posts API.
"""
from rest_framework import viewsets, authentication, permissions
from core.models import Post, Comment, User
from post.serializers import PostSerializer, CommentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class PostViewSet(viewsets.ModelViewSet):
    """Manage posts in the database."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapan kullanıcılar görebilir.

    def perform_create(self, serializer):
        """Create a new post."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Belirli bir postun yorumlarını listele."""
        post = self.get_object()
        comments = post.comments.all()  # İlgili yorumları al
        return Response(CommentSerializer(comments, many=True).data)


    @action(detail=True, methods=['get'], url_path='user_posts')
    def user_posts(self, request, pk=None):
        """Get all posts items for a specific user by user_id."""
        if not User.objects.filter(id=pk).exists():
            return Response(
                {"detail": "Belirtilen user_id'ye sahip bir kullanıcı bulunamadı."},
                status=404
            )
        posts = Post.objects.filter(user__id=pk)
        # Serileştirme işlemi
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """Manage comments in the database."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]  # Sadece giriş yapan kullanıcılar görebilir.

    def perform_create(self, serializer):
        """Create a new comment."""
        user = self.request.user  # Oturum açmış kullanıcıyı alıyoruz
        serializer.save(user=user)
    @action(detail=True, methods=['get'], url_path='filter-by-post')
    def filter_by_post(self, request, pk=None):
        """Filter comments by post ID."""
        if not Post.objects.filter(id=pk).exists():
            return Response(
                {"detail": "Belirtilen post_id'ye sahip bir post bulunamadı."},
                status=404
            )
        comments = Comment.objects.filter(post__id=pk)

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)