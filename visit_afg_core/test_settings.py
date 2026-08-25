from .settings import *  # noqa: F401,F403


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# This legacy project currently has no migrations for its local apps. Disabling
# migrations in tests lets Django build all installed models in dependency order
# without touching the development PostgreSQL database.
MIGRATION_MODULES = {
    'account': None,
    'admin': None,
    'auth': None,
    'contenttypes': None,
    'sessions': None,
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

STRIPE_PUBLIC_KEY = 'pk_test_customer_portal'
STRIPE_SECRET_KEY = 'sk_test_customer_portal'
STRIPE_WEBHOOK_SECRET = 'whsec_customer_portal'
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
