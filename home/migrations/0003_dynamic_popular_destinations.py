from django.db import migrations, models
from django.utils import timezone


DESTINATIONS = (
    (
        "Kabul",
        "Kabul",
        "states:kabul",
        "image_for_province/kabul.jpeg",
        "Historic gardens, museums, markets, and the capital's living culture.",
    ),
    (
        "Bamyan",
        "Bamyan",
        "states:bamyan",
        "image_for_province/bamyan2.jpg",
        "Cliff landscapes, archaeological heritage, and the lakes of Band-e Amir.",
    ),
    (
        "Herat",
        "Herat",
        "states:Herat",
        "image_for_province/Herat16.jpg",
        "Timurid architecture, the citadel, tilework, and western Afghan traditions.",
    ),
    (
        "Balkh",
        "Balkh",
        "states:balkh",
        "image_for_province/balkh.jpeg",
        "Ancient Balkh and the Blue Mosque of Mazar-e Sharif.",
    ),
    (
        "Nangarhar",
        "Nangarhar",
        "states:Nangarhar",
        "image_for_province/nangrher.jpeg",
        "Jalalabad, green valleys, gardens, and eastern Afghan hospitality.",
    ),
    (
        "Kandahar",
        "Kandahar",
        "states:Kandahar",
        "image_for_province/kandher.jpg",
        "Landmarks of Afghan history, traditional bazaars, and the Arghandab valley.",
    ),
    (
        "Ghor",
        "Ghor",
        "states:Ghor",
        "image_for_province/ghor.jpeg",
        "Mountain scenery and the UNESCO-listed Minaret of Jam.",
    ),
    (
        "Badakhshan",
        "Badakhshan",
        "states:Badakhshan",
        "image_for_province/Badakhshan3.jpg",
        "The Wakhan Corridor, high mountains, and remote communities.",
    ),
)


def seed_popular_destinations(apps, schema_editor):
    PopularPlace = apps.get_model("home", "PopularPlace")
    for display_order, item in enumerate(DESTINATIONS, start=1):
        title, province, url_name, static_image, description = item
        PopularPlace.objects.get_or_create(
            title=title,
            defaults={
                "province": province,
                "url_name": url_name,
                "static_image": static_image,
                "description": description,
                "display_order": display_order,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("home", "0002_popularplace_placeimage")]
    operations = [
        migrations.AlterModelOptions(
            name="popularplace",
            options={
                "ordering": ("display_order", "title", "pk"),
                "verbose_name": "Popular destination",
                "verbose_name_plural": "Popular destinations",
            },
        ),
        migrations.AlterField(
            model_name="popularplace",
            name="title",
            field=models.CharField(max_length=200, verbose_name="Destination name"),
        ),
        migrations.AlterField(
            model_name="popularplace",
            name="preview_image",
            field=models.ImageField(
                blank=True,
                upload_to="places/previews/",
                verbose_name="Uploaded card image",
            ),
        ),
        migrations.AlterField(
            model_name="popularplace",
            name="description",
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name="Short description",
            ),
        ),
        migrations.AlterField(
            model_name="placeimage",
            name="image",
            field=models.ImageField(
                upload_to="places/gallery/",
                verbose_name="Gallery image",
            ),
        ),
        migrations.AddField(
            model_name="popularplace",
            name="static_image",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Optional path inside the static folder. The uploaded card image "
                    "takes priority when both are set."
                ),
                max_length=255,
                verbose_name="Bundled static image",
            ),
        ),
        migrations.AddField(
            model_name="popularplace",
            name="url_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text="For example: states:kabul or states:Nangarhar",
                max_length=150,
                verbose_name="Django URL name",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="popularplace",
            name="external_url",
            field=models.URLField(
                blank=True,
                help_text=(
                    "Optional. When supplied, this link is used instead of the "
                    "Django URL name."
                ),
                verbose_name="External URL",
            ),
        ),
        migrations.AddField(
            model_name="popularplace",
            name="display_order",
            field=models.PositiveIntegerField(
                db_index=True,
                default=0,
                verbose_name="Display order",
            ),
        ),
        migrations.AddField(
            model_name="popularplace",
            name="is_active",
            field=models.BooleanField(
                db_index=True,
                default=True,
                verbose_name="Active",
            ),
        ),
        migrations.AddField(
            model_name="popularplace",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="popularplace",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.RunPython(seed_popular_destinations, migrations.RunPython.noop),
    ]
