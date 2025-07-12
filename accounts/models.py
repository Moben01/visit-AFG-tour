from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    type_of_customer = models.CharField(
        max_length=15,
        choices=[
            ('Tourist', 'Tourist'),
            ('Guide', 'Guide'),
            ('Translator', 'Translator'),
            ('Operator', 'Operator'),
            ('Moderator', 'Moderator'),
        ],
        default='Tourist'
    )