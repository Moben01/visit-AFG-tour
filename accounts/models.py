# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)

    CHOICES = [
        ('Tourist', 'Tourist'),
        ('Guide', 'Guide'),
        ('Translator', 'Translator'),
        ('Operator', 'Operator'),
        ('Moderator', 'Moderator'),
    ]
    my_choice_field = models.CharField(max_length=20, choices=CHOICES, blank=True, null=True, default="Tourist")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='accounts_customuser_email_ci_uniq',
            ),
        ]

    def clean(self):
        super().clean()
        self.email = (self.email or '').strip().lower()

    def save(self, *args, **kwargs):
        self.email = (self.email or '').strip().lower()
        return super().save(*args, **kwargs)
