from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import handler404  # optional, for clarity

# Custom error handlers (MUST be here — project-level only)
handler404 = 'home.views.custom_404_view'

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # For language switching
]


urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls', namespace='home')),
    path('states/', include('states.urls', namespace='states')),
)

# Include Rosetta only if DEBUG = True (recommended)
if settings.DEBUG:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls')),  # ✅ Rosetta admin panel
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)