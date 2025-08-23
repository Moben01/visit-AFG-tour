from django.db import models

# Create your models here.
class Main_things(models.Model):
    noumber = models.CharField(max_length=100)
    email =models.CharField(max_length=100)











# app/models.py
from django.db import models

class PopularPlace(models.Model):
    title = models.CharField(max_length=200, verbose_name="Place Name")
    province = models.CharField(max_length=100, verbose_name="Province", blank=True, null=True)
    preview_image = models.ImageField(upload_to="places/previews/", verbose_name="Preview Image")
    description = models.TextField(verbose_name="Description", blank=True, null=True)

    def __str__(self):
        return self.title


class PlaceImage(models.Model):
    place = models.ForeignKey(PopularPlace, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="places/gallery/", verbose_name="Gallery Image")

    def __str__(self):
        return f"Image for {self.place.title}"
