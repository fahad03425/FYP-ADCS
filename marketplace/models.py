# marketplace/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random

class CustomUser(AbstractUser):
    userid = models.IntegerField(unique=True, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    isActive = models.BooleanField(default=True)
    isSeller = models.BooleanField(default=False)
    CreateDateTime = models.DateTimeField(default=timezone.now)
    Lastupdate = models.DateTimeField(auto_now=True)

    # Use unique related_names for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Set a unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Set a unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def save(self, *args, **kwargs):
        if not self.userid:
            self.userid = random.randint(100000, 999999)
        if not self.username:
            self.username = f'user_{self.userid}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username



