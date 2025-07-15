# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    CHOICES = [
        ('Tourist', 'Tourist'),
        ('Guide', 'Guide'),
        ('Translator', 'Translator'),
        ('Operator', 'Operator'),
        ('Moderator', 'Moderator'),
    ]
    my_choice_field = models.CharField(max_length=20, choices=CHOICES, blank=True, null=True, default="Tourist")
