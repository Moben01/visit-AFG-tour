import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_dynamic_popular_destinations'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.SlugField(help_text='Stable identifier used by templates, for example home_destinations.', max_length=100, unique=True)),
                ('name', models.CharField(help_text='Internal management label.', max_length=150)),
                ('eyebrow', models.CharField(blank=True, max_length=150)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('body', models.TextField(blank=True)),
                ('button_label', models.CharField(blank=True, max_length=120)),
                ('button_url_name', models.CharField(blank=True, help_text='Optional named Django URL, for example home:search.', max_length=150)),
                ('button_external_url', models.URLField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to='content/sections/')),
                ('static_image', models.CharField(blank=True, max_length=255)),
                ('display_order', models.PositiveIntegerField(db_index=True, default=0)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('display_order', 'name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='ManagedMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to='content/library/%Y/%m/')),
                ('alt_text', models.CharField(blank=True, max_length=255)),
                ('category', models.CharField(choices=[('image', 'Image'), ('document', 'Document'), ('video', 'Video'), ('other', 'Other')], default='image', max_length=20)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Managed media',
                'ordering': ('-created_at', 'title'),
            },
        ),
        migrations.CreateModel(
            name='ProvincePage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(max_length=160, unique=True)),
                ('summary', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('hero_image', models.ImageField(blank=True, upload_to='provinces/heroes/')),
                ('static_hero_image', models.CharField(blank=True, help_text='Optional path inside the static folder.', max_length=255)),
                ('meta_title', models.CharField(blank=True, max_length=255)),
                ('meta_description', models.CharField(blank=True, max_length=320)),
                ('is_published', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('name', 'pk'),
            },
        ),
        migrations.AlterModelOptions(
            name='main_things',
            options={'verbose_name': 'Site contact', 'verbose_name_plural': 'Site contact'},
        ),
        migrations.CreateModel(
            name='ContentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=200)),
                ('body', models.TextField(blank=True)),
                ('icon_class', models.CharField(blank=True, help_text='Optional icon CSS classes, for example fa-solid fa-bed.', max_length=150)),
                ('image', models.ImageField(blank=True, upload_to='content/items/')),
                ('static_image', models.CharField(blank=True, max_length=255)),
                ('link_label', models.CharField(blank=True, max_length=120)),
                ('url_name', models.CharField(blank=True, max_length=150)),
                ('external_url', models.URLField(blank=True)),
                ('display_order', models.PositiveIntegerField(db_index=True, default=0)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='home.contentsection')),
            ],
            options={
                'ordering': ('display_order', 'title', 'pk'),
            },
        ),
        migrations.AddField(
            model_name='popularplace',
            name='province_page',
            field=models.ForeignKey(blank=True, help_text='Optional dynamic province page managed in Website Content.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='popular_cards', to='home.provincepage'),
        ),
        migrations.CreateModel(
            name='ProvincePageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('image', models.ImageField(blank=True, upload_to='provinces/sections/')),
                ('static_image', models.CharField(blank=True, max_length=255)),
                ('display_order', models.PositiveIntegerField(db_index=True, default=0)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='home.provincepage')),
            ],
            options={
                'ordering': ('display_order', 'heading', 'pk'),
            },
        ),
    ]
