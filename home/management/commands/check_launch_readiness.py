from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from home.homepage import public_featured_tours
from home.models import Main_things


class Command(BaseCommand):
    help = "Check whether verified brand data and enough published featured tours are ready for launch."

    def handle(self, *args, **options):
        try:
            configuration = Main_things.get_solo()
            failures = []

            if not configuration.is_public_ready:
                failures.append(
                    "Missing required public settings: "
                    + ", ".join(configuration.missing_required_public_field_labels)
                )

            minimum_tours = configuration.minimum_featured_tours_for_launch
            ready_tours = public_featured_tours()
            if len(ready_tours) < minimum_tours:
                failures.append(
                    "Complete published featured tours: "
                    f"{len(ready_tours)}/{minimum_tours}"
                )
        except DatabaseError as error:
            raise CommandError(
                "The database schema is not ready for launch checks. Apply the "
                "reviewed home migrations before running this command."
            ) from error

        if failures:
            for failure in failures:
                self.stdout.write(f"FAIL: {failure}")
            raise CommandError("Site launch readiness checks failed.")

        self.stdout.write(
            self.style.SUCCESS(
                "Site launch readiness passed: public settings complete and "
                f"{len(ready_tours)} featured tours ready."
            )
        )
