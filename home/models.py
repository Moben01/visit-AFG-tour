from django.db import models

# Create your models here.
class Main_things(models.Model):
    noumber = models.CharField(max_length=100)
    email =models.CharField(max_length=100)