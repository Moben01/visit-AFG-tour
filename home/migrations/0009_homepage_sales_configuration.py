import django.core.validators
import django.db.models.deletion
import home.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0008_rebrand_public_content"),
        ("tour", "__first__"),
    ]

    operations = [
        migrations.AddField(
            model_name="main_things",
            name="enabled_hosting_services",
            field=models.JSONField(
                blank=True,
                default=home.models.default_enabled_hosting_services,
            ),
        ),
        migrations.AddField(
            model_name="main_things",
            name="minimum_featured_tours_for_launch",
            field=models.PositiveSmallIntegerField(
                default=3,
                help_text=(
                    "Minimum complete, published homepage features required "
                    "before launch."
                ),
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(12),
                ],
            ),
        ),
        migrations.CreateModel(
            name="TourHomepageFeature",
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
                    "physical_level",
                    models.CharField(
                        choices=[
                            ("easy", "Easy"),
                            ("moderate", "Moderate"),
                            ("active", "Active"),
                            ("challenging", "Challenging"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "display_order",
                    models.PositiveIntegerField(db_index=True, default=0),
                ),
                (
                    "is_active",
                    models.BooleanField(db_index=True, default=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tour",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="homepage_feature",
                        to="tour.tour",
                    ),
                ),
            ],
            options={
                "verbose_name": "Homepage tour feature",
                "verbose_name_plural": "Homepage tour features",
                "ordering": ("display_order", "tour__title", "pk"),
            },
        ),
    ]
