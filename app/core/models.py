"""
Database models
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """ Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """ Create, save and return a new user."""
        if not email:
            raise ValueError('Email must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Company(models.Model):
    """Company information."""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Geo(models.Model):
    lat = models.DecimalField(max_digits=12, decimal_places=9, blank=True)
    lng = models.DecimalField(max_digits=12, decimal_places=9, blank=True)

    def __str__(self):
        return f"({self.lat}, {self.lng})"

class Address(models.Model):
    """Address details."""
    street = models.CharField(max_length=255)
    suite = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    geo = models.ForeignKey('Geo', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.street}, {self.city}"

class User(AbstractBaseUser, PermissionsMixin):
    """ User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)  # username alanı eklendi
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)  # phone ekledik
    website = models.CharField(max_length=255, blank=True)  # website ekledik
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)  # address alanı
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)  # company ilişkisi

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Kullanıcı modeliyle ilişki
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.title


# Comment Model
class Comment(models.Model):
    postId = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_comments',
    )
    body = models.TextField()

    def __str__(self):
        return f"Comment on {self.postId.title}"

    @property
    def name(self):
        """Get the name of the user who commented."""
        return self.user.name if self.user else None

    @property
    def email(self):
        """Get the email of the user who commented."""
        return self.user.email if self.user else None


class Album(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Kullanıcı modeliyle ilişki
        on_delete=models.CASCADE,
        related_name='albums'
    )
    title = models.CharField(max_length=255, unique=True, blank=False)

    def __str__(self):
        return self.title

class Photo(models.Model):
    albumId = models.ForeignKey(Album, related_name="photos", on_delete=models.CASCADE)
    user = models.ForeignKey(
        'User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_photos',
    )
    title = models.CharField(max_length=255)
    url = models.URLField()
    thumbnailUrl = models.URLField()


    def __str__(self):
        return f"Album on {self.albumId.title}"

    @property
    def email(self):
        """Get the email of the user who Photo."""
        return self.user.email if self.user else None


class ToDo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Kullanıcı modeliyle ilişki
        on_delete=models.CASCADE,
        related_name='todo'
    )
    title = models.CharField(max_length=255)
    completed = models.BooleanField()

    def __str__(self):
        return self.title