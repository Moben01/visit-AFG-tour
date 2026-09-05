import json
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from home.branding import DATABASE_REPLACEMENT_FIELDS, replace_brand_terms
from home.management.commands.audit_legacy_branding import scan_database


def collect_proposed_changes(alias="default"):
    findings, warnings = scan_database(
        alias=alias, field_registry=DATABASE_REPLACEMENT_FIELDS
    )
    affected = {(item.model, item.field, item.record_id) for item in findings}
    changes = []
    for model_label, field_name, record_id in sorted(
        affected, key=lambda item: (item[0], str(item[2]), item[1])
    ):
        model = apps.get_model(model_label)
        row = (
            model.objects.using(alias)
            .filter(pk=record_id)
            .values("pk", field_name)
            .first()
        )
        if not row:
            continue
        old_value = row[field_name]
        new_value = replace_brand_terms(old_value)
        if new_value != old_value:
            changes.append(
                {
                    "model": model_label,
                    "field": field_name,
                    "record_id": record_id,
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )
    return changes, warnings


def write_backup(changes):
    backup_directory = (
        Path(settings.BASE_DIR) / "var" / "backups" / "legacy-branding"
    )
    backup_directory.mkdir(parents=True, exist_ok=True)
    version = timezone.now().strftime("%Y%m%dT%H%M%S%fZ")
    path = backup_directory / f"legacy-branding-{version}.json"
    payload = {
        "schema_version": 1,
        "created_at": timezone.now().isoformat(),
        "command": "replace_legacy_branding --apply",
        "changes": changes,
    }
    with path.open("x", encoding="utf-8") as backup_file:
        json.dump(payload, backup_file, ensure_ascii=False, indent=2, default=str)
        backup_file.write("\n")
    return path


class Command(BaseCommand):
    help = "Preview or apply approved database-backed legacy-brand replacements."

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview proposed changes (the default).",
        )
        mode.add_argument(
            "--apply",
            action="store_true",
            help="Back up and apply the approved field-level changes.",
        )

    def handle(self, *args, **options):
        changes, warnings = collect_proposed_changes()
        for warning in warnings:
            self.stderr.write(self.style.WARNING(f"schema warning: {warning}"))
        for change in changes:
            self.stdout.write(
                f"model={change['model']} field={change['field']} "
                f"id={change['record_id']} "
                f"old={json.dumps(change['old_value'], ensure_ascii=False)} "
                f"new={json.dumps(change['new_value'], ensure_ascii=False)}"
            )

        if not options["apply"]:
            self.stdout.write(
                f"Dry run only: {len(changes)} field change(s) proposed; "
                "no backup created and no data modified."
            )
            return
        if not changes:
            self.stdout.write(self.style.SUCCESS("No approved database changes required."))
            return

        backup_path = write_backup(changes)
        try:
            with transaction.atomic():
                for change in changes:
                    model = apps.get_model(change["model"])
                    updated = model.objects.filter(
                        pk=change["record_id"],
                        **{change["field"]: change["old_value"]},
                    ).update(**{change["field"]: change["new_value"]})
                    if updated != 1:
                        raise CommandError(
                            "A proposed value changed before apply; the transaction "
                            "was rolled back. Review the backup and rerun dry-run."
                        )
        except Exception:
            self.stderr.write(f"Backup retained at {backup_path}")
            raise

        self.stdout.write(f"Backup written to {backup_path}")
        self.stdout.write(
            self.style.SUCCESS(
                f"Applied {len(changes)} approved field-level replacement(s)."
            )
        )
