"""
Tests for the todo API.
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import ToDo
from rest_framework.test import APIClient

ToDo_URL = '/api/todo/'


class ToDoViewSetTest(APITestCase):
    """Test the ToDo API endpoints"""

    def setUp(self):
        """Create user and a sample ToDo for testing."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123'
        )
        self.todo = ToDo.objects.create(
            user=self.user,
            title="Test ToDo",
            completed=False,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_todos_for_authenticated_user(self):
        """Test retrieving to-do list for authenticated user"""
        # Adjust this to your URL
        response = self.client.get(ToDo_URL)
        todos = ToDo.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), todos.count())

    def test_create_todo_for_authenticated_user(self):
        """Test creating a new to-do item."""
        data = {
            "title": "New ToDo",
            "completed": False,
        }
        response = self.client.post(ToDo_URL, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ToDo.objects.count(), 2)
        self.assertEqual(ToDo.objects.latest('id').title, "New ToDo")

    def test_get_user_todos(self):
        """Test retrieving all to-dos for a specific user."""
        url = f'/api/todo/{self.user.id}/user_todos/'
        response = self.client.get(url)
        todos = ToDo.objects.filter(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), todos.count())

    def test_user_todos_not_found(self):
        """Test that a 404 is returned if the user does not exist."""
        invalid_user_id = 9999
        url = f'/api/todo/{invalid_user_id}/user_todos/'  # User ID that doesn't exist
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Belirtilen user_id'ye sahip bir kullanıcı bulunamadı.")

    def test_unauthenticated_user_access(self):
        """Test that unauthenticated users cannot access to-do items."""
        self.client.logout()  # Logout to make the client unauthenticated
        response = self.client.get(ToDo_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_todo(self):
        """Test deleting a specific to-do."""
        url = f'{ToDo_URL}{self.todo.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ToDo.objects.filter(id=self.todo.id).count(), 0)

    def test_update_todo_with_patch(self):
        """Test partially updating a to-do (PATCH)."""
        url = f'{ToDo_URL}{self.todo.id}/'
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()  # Veritabanından güncellenen veriyi al
        self.assertEqual(self.todo.title, "Updated Title")

    def test_update_todo_with_put(self):
        """Test updating a to-do completely (PUT)."""
        url = f'{ToDo_URL}{self.todo.id}/'
        data = {
            "title": "Completely Updated Title",
            "completed": True,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()  # Veritabanından güncellenen veriyi al
        self.assertEqual(self.todo.title, "Completely Updated Title")
        self.assertEqual(self.todo.completed, True)

    def test_delete_todo_unauthorized(self):
        """Test that an unauthenticated user cannot delete a to-do."""
        self.client.logout()
        url = f'{ToDo_URL}{self.todo.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(ToDo.objects.filter(id=self.todo.id).exists())  # To-Do hâlâ duruyor mu?

    def test_patch_todo_unauthorized(self):
        """Test that an unauthenticated user cannot patch a to-do."""
        self.client.logout()
        url = f'{ToDo_URL}{self.todo.id}/'
        data = {"title": "Unauthorized Update"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.todo.refresh_from_db()
        self.assertNotEqual(self.todo.title, "Unauthorized Update")

    def test_put_todo_unauthorized(self):
        """Test that an unauthenticated user cannot update a to-do."""
        self.client.logout()
        url = f'{ToDo_URL}{self.todo.id}/'
        data = {
            "title": "Unauthorized Full Update",
            "completed": True,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.todo.refresh_from_db()
        self.assertNotEqual(self.todo.title, "Unauthorized Full Update")
        self.assertNotEqual(self.todo.completed, "Unauthorized completed")
