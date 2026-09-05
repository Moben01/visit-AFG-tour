import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("home", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="PopularPlace",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Place Name")),
                (
                    "province",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Province",
                    ),
                ),
                (
                    "preview_image",
                    models.ImageField(
                        upload_to="places/previews/",
                        verbose_name="Preview Image",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PlaceImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to="places/gallery/",
                        verbose_name="Gallery Image",
                    ),
                ),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="home.popularplace",
                    ),
                ),
            ],
        ),
    ]
