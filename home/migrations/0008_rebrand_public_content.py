from django.db import migrations


FORWARD_CHANGES = (
    (
        "home_map_hero",
        "title",
        "Every Journey Together",
        "Your Local Host in Afghanistan",
    ),
    (
        "home_benefits",
        "eyebrow",
        "Why AfghanAwaits",
        "Why Larmoond Travel and Tours",
    ),
    (
        "home_trust",
        "body",
        "AfghanAwaits connects information, booking details, and local operations in one clear workflow.",
        "Larmoond Travel and Tours connects information, booking details, and local operations in one clear workflow.",
    ),
    (
        "home_professionals",
        "title",
        "Share your expertise through AfghanAwaits",
        "Share your expertise through Larmoond Travel and Tours",
    ),
)


def _apply_changes(apps, changes):
    ContentSection = apps.get_model("home", "ContentSection")
    for key, field_name, old_value, new_value in changes:
        ContentSection.objects.filter(
            key=key,
            **{field_name: old_value},
        ).update(**{field_name: new_value})


def rebrand_public_content(apps, schema_editor):
    _apply_changes(apps, FORWARD_CHANGES)


def restore_legacy_public_content(apps, schema_editor):
    reverse_changes = tuple(
        (key, field_name, new_value, old_value)
        for key, field_name, old_value, new_value in reversed(FORWARD_CHANGES)
    )
    _apply_changes(apps, reverse_changes)


class Migration(migrations.Migration):
    dependencies = [("home", "0007_site_and_brand_configuration")]
    operations = [
        migrations.RunPython(
            rebrand_public_content,
            restore_legacy_public_content,
        )
    ]
