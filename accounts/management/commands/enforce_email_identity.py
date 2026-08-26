from collections import defaultdict

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Normalize account emails, sync Allauth addresses, and enforce case-insensitive uniqueness.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        users = list(user_model.objects.order_by('pk'))
        normalized_users = []
        grouped = defaultdict(list)
        blank_users = []

        for user in users:
            email = (user.email or '').strip().lower()
            if not email:
                blank_users.append(user.username or str(user.pk))
                continue
            grouped[email].append(user.username or str(user.pk))
            normalized_users.append((user, email))

        duplicates = {
            email: usernames for email, usernames in grouped.items()
            if len(usernames) > 1
        }
        if blank_users:
            raise CommandError(
                'Users without email must be fixed first: ' + ', '.join(blank_users)
            )
        if duplicates:
            details = '; '.join(
                f"{email}: {', '.join(usernames)}"
                for email, usernames in duplicates.items()
            )
            raise CommandError('Duplicate account emails must be fixed first: ' + details)

        with transaction.atomic():
            for user, email in normalized_users:
                if user.email != email:
                    user_model.objects.filter(pk=user.pk).update(email=email)
                EmailAddress.objects.filter(user=user).exclude(
                    email__iexact=email
                ).update(primary=False)
                address = EmailAddress.objects.filter(
                    user=user, email__iexact=email
                ).first()
                if address is None:
                    address = EmailAddress(user=user, email=email)
                address.email = email
                address.primary = True
                address.save()

        constraint_name = 'accounts_customuser_email_ci_uniq'
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(
                cursor, user_model._meta.db_table
            )
        if constraint_name not in constraints:
            constraint = next(
                item for item in user_model._meta.constraints
                if item.name == constraint_name
            )
            with connection.schema_editor() as schema_editor:
                schema_editor.add_constraint(user_model, constraint)
            self.stdout.write(self.style.SUCCESS('Added case-insensitive email uniqueness.'))

        self.stdout.write(self.style.SUCCESS(
            f'Email identity is ready for {len(normalized_users)} account(s).'
        ))
