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

    def test_invalid_comment_creation(self):
        """Test creating a comment with invalid data."""
        url = '/api/comments/'
        data = {'postId': None, 'body': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('postId', response.data)
        self.assertIn('body', response.data)

    def test_delete_post(self):
        """Test deleting a user's post."""
        url = f'/api/posts/{self.post.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_update_post(self):
        """Test that a user can update post."""
        url = f'/api/posts/{self.post.id}/'
        data = {'title': 'Updated Title', 'body': 'Updated Body'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, data['title'])
        self.assertEqual(self.post.body, data['body'])

    def test_create_post_unauthenticated(self):
        """Test that unauthenticated users cannot create posts."""
        self.client.credentials()  # Token'ı temizle
        url = '/api/posts/'
        data = {'title': 'Unauthorized Post', 'body': 'Should not be created'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment(self):
        """Test that a user can update their own comment."""
        url = f'/api/comments/{self.comment.id}/'
        data = {'body': 'Updated comment body'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.body, data['body'])

    def test_delete_comment(self):
        """Test that a user can delete their own comment."""
        url = f'/api/comments/{self.comment.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_filter_comments_by_nonexistent_post(self):
        """Var olmayan bir post ID için yorum filtreleme testi."""
        invalid_post_id = 9999
        url = f'/api/comments/{invalid_post_id}/filter-by-post/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Belirtilen post_id'ye sahip bir post bulunamadı.")

    def test_filter_comments_unauthenticated(self):
        """Kimlik doğrulaması yapılmadan yorumları filtreleme testi."""
        self.client.credentials()  # Authorization header'ı kaldır
        url = f'/api/comments/{self.post.id}/filter-by-post/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', str(response.data))

    def test_filter_comments_by_post_success(self):
        """Belirli bir post ile ilişkili yorumları filtreleme testi."""
        url = f'/api/comments/?postId={self.post.id}/filter-by-post/'  # Doğru alan adı olan `postId` kullanılıyor
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Yalnızca bir yorum olmalı
        self.assertEqual(response.data[0]['body'], self.comment.body)
        self.assertEqual(response.data[0]['postId'], self.post.id)

    def test_get_user_posts_success(self):
        """Belirli bir kullanıcıya ait postları alma testi."""
        url = f'/api/posts/{self.user.id}/user_posts/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Kullanıcının bir postu olmalı
        self.assertEqual(response.data[0]['title'], self.post.title)
        self.assertEqual(int(response.data[0]['userId']), self.user.id)

    def test_get_user_posts_invalid_user(self):
        """Geçersiz bir user ID ile post alma testi."""
        invalid_user_id = 9999
        url = f'/api/posts/{invalid_user_id}/user_posts/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Belirtilen user_id'ye sahip bir kullanıcı bulunamadı.")

    def test_get_user_posts_unauthenticated(self):
        """Kimlik doğrulaması yapılmadan kullanıcı postlarını alma testi."""
        self.client.credentials()  # Authorization header'ı kaldır
        url = f'/api/posts/{self.user.id}/user_posts/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', str(response.data))

    def test_get_post_comments_success(self):
        """Belirli bir postun yorumlarını alma testi."""
        url = f'/api/posts/{self.post.id}/comments/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # İlk başta yalnızca bir yorum olmalı
        self.assertEqual(response.data[0]['body'], self.comment.body)
        self.assertEqual(response.data[0]['postId'], self.post.id)

    def test_get_post_comments_invalid_post(self):
        """Geçersiz bir post ID ile yorum alma testi."""
        invalid_post_id = 9999
        url = f'/api/posts/{invalid_post_id}/comments/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Not found.")

    def test_get_post_comments_unauthenticated(self):
        """Kimlik doğrulaması yapılmadan post yorumlarını alma testi."""
        self.client.credentials()  # Authorization header'ı kaldır
        url = f'/api/posts/{self.post.id}/comments/'
        response = self.client.get(url)

        # Doğrulamalar
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', str(response.data))
