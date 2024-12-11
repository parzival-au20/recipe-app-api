"""
URL mappings for to-do API
"""


from rest_framework.routers import DefaultRouter
from todo.views import ToDoViewSet

app_name = 'todo'


router = DefaultRouter()
router.register('todo', ToDoViewSet)

urlpatterns = [
    # Diğer URL'ler
] + router.urls
