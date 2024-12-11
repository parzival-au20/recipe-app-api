"""
Tests for the post API.
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import Post, Comment
from django.urls import reverse
from rest_framework.test import APIClient


class PostTests(APITestCase):

    def setUp(self):
        """Test için gerekli verileri oluşturuyoruz."""
        # Kullanıcı oluşturma
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(email="user@example.com", password='testpassword')

        # Get token for authentication
        token_url = reverse('user:token')
        response = self.client.post(token_url, {
            'email': 'user@example.com',
            'password': 'testpassword'
        })

        self.token = response.data.get('token')  # Token'dan `token` alın
        self.assertIsNotNone(self.token, "Token alınamadı!")

        # Add token to authorization header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Post oluşturma
        self.post = Post.objects.create(
            title="Test Post",
            body="This is a test post",
            user=self.user
        )

        # Yorum oluşturma
        self.comment = Comment.objects.create(
            postId=self.post,
            body="This is a test comment"
        )

    def test_create_post(self):
        """Yeni bir post oluşturma."""
        url = '/api/posts/'
        data = {'title': 'New Post', 'body': 'Post body', 'user': self.user.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)  # Bir post daha olmalı

    def test_get_posts(self):
        """Postları listeleme."""
        url = '/api/posts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # İlk başta sadece bir post olmalı

    def test_get_post_detail(self):
        """Post detayını alma."""
        url = f'/api/posts/{self.post.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)

    def test_create_comment(self):
        """Bir post için yorum ekleme."""
        url = '/api/comments/'
        data = {
            'postId': self.post.id,  # Yorumun hangi postla ilişkili olduğunu belirtiyoruz
            'body': 'This is a test comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)  # Bir yorum daha olmalı

    def test_get_comments(self):
        """Bir postun yorumlarını listeleme."""
        url = f'/api/posts/{self.post.id}/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Yalnızca bir yorum olmalı

    def test_filter_comments_by_post(self):
        """Bir post ile ilişkili yorumları getirme."""
        url = f'/api/comments/?postId={self.post.id}'  # Yorumları postId'ye göre filtrele
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Sadece bir yorum olmalı

    def test_invalid_user_id(self):
        """Geçersiz user_id ile yorum alma."""
        url = '/api/comments/9999/filter-by-post/'  # Böyle bir post id'si olmayacak
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Belirtilen post_id'ye sahip bir post bulunamadı.")
