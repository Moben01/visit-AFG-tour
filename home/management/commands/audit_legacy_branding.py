from dataclasses import dataclass
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, connections

from home.branding import DATABASE_AUDIT_FIELDS, iter_brand_matches
from home.legacy_brand_allowlist import find_allowlist_rule


TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".po",
    ".py",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
SKIPPED_DIRECTORIES = {
    ".git",
    ".venv",
    ".codex-deploy",
    "__pycache__",
    "media",
    "staticfiles",
    "var",
}
SECRET_NAMES = {
    ".env",
    "credentials.json",
    "local_settings.py",
    "secrets.json",
}
SECRET_SUFFIXES = {".key", ".p12", ".pem", ".pfx"}


@dataclass(frozen=True)
class SourceFinding:
    path: str
    line_number: int | None
    term: str
    kind: str = "content"


@dataclass(frozen=True)
class DatabaseFinding:
    model: str
    field: str
    record_id: object
    term: str


def _is_secret_path(path):
    lowered_names = {part.lower() for part in path.parts}
    name = path.name.lower()
    return (
        bool(lowered_names & SECRET_NAMES)
        or name.startswith(".env.")
        or path.suffix.lower() in SECRET_SUFFIXES
        or "credential" in name
        or "secret" in name
    )


def scan_source_tree(root):
    findings = []
    allowlisted = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIPPED_DIRECTORIES for part in relative.parts):
            continue
        if _is_secret_path(relative):
            continue
        relative_name = relative.as_posix()

        for term in dict.fromkeys(iter_brand_matches(relative_name)):
            rule = find_allowlist_rule(relative_name, term, relative_name)
            finding = SourceFinding(relative_name, None, term, "filename")
            (allowlisted if rule else findings).append((finding, rule))

        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        for line_number, line in enumerate(lines, start=1):
            for term in dict.fromkeys(iter_brand_matches(line)):
                rule = find_allowlist_rule(relative_name, term, line)
                finding = SourceFinding(relative_name, line_number, term)
                (allowlisted if rule else findings).append((finding, rule))
    return findings, allowlisted


def _physical_fields(connection, model, field_names, cursor):
    columns = {
        description.name
        for description in connection.introspection.get_table_description(
            cursor, model._meta.db_table
        )
    }
    return tuple(
        field_name
        for field_name in field_names
        if model._meta.get_field(field_name).column in columns
    )


def scan_database(alias="default", field_registry=None):
    field_registry = field_registry or DATABASE_AUDIT_FIELDS
    connection = connections[alias]
    findings = []
    warnings = []
    try:
        tables = set(connection.introspection.table_names())
        with connection.cursor() as cursor:
            for model_label, field_names in field_registry.items():
                model = apps.get_model(model_label)
                if model._meta.db_table not in tables:
                    warnings.append(f"table missing for {model_label}")
                    continue
                physical_fields = _physical_fields(
                    connection, model, field_names, cursor
                )
                missing = tuple(name for name in field_names if name not in physical_fields)
                if missing:
                    warnings.append(
                        f"{model_label} fields unavailable in current schema: "
                        + ", ".join(missing)
                    )
                if not physical_fields:
                    continue
                for row in model.objects.using(alias).values(
                    "pk", *physical_fields
                ).iterator():
                    for field_name in physical_fields:
                        value = row.get(field_name) or ""
                        for term in dict.fromkeys(iter_brand_matches(str(value))):
                            findings.append(
                                DatabaseFinding(
                                    model_label, field_name, row["pk"], term
                                )
                            )
    except DatabaseError as error:
        raise CommandError(
            "Database branding audit could not complete. No data was modified."
        ) from error
    return findings, warnings


class Command(BaseCommand):
    help = "Read-only audit for prohibited public legacy branding."

    def add_arguments(self, parser):
        parser.add_argument(
            "--show-allowlisted",
            action="store_true",
            help="Show permitted historical/infrastructure occurrences.",
        )

    def handle(self, *args, **options):
        source_findings, allowlisted = scan_source_tree(Path(settings.BASE_DIR))
        database_findings, warnings = scan_database()

        for finding, _rule in source_findings:
            location = (
                f"{finding.path}:{finding.line_number}"
                if finding.line_number
                else finding.path
            )
            self.stdout.write(
                f"file={location} kind={finding.kind} term={finding.term!r}"
            )
        for finding in database_findings:
            self.stdout.write(
                "database "
                f"model={finding.model} field={finding.field} "
                f"id={finding.record_id} term={finding.term!r}"
            )
        for warning in warnings:
            self.stderr.write(self.style.WARNING(f"schema warning: {warning}"))

        if options["show_allowlisted"]:
            for finding, rule in allowlisted:
                location = (
                    f"{finding.path}:{finding.line_number}"
                    if finding.line_number
                    else finding.path
                )
                self.stdout.write(
                    "allowlisted "
                    f"file={location} category={rule.category} term={finding.term!r}"
                )

        count = len(source_findings) + len(database_findings)
        if count:
            raise CommandError(
                f"Legacy branding audit failed: {count} public occurrence(s) found."
            )
        self.stdout.write(
            self.style.SUCCESS(
                "Legacy branding audit passed: no public legacy terms found."
            )
        )
