from io import StringIO
import json
from pathlib import Path
import tempfile

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .branding import iter_brand_matches
from .models import ContentSection, Main_things
from .views import custom_500_view


class LegacyBrandAuditCommandTests(TestCase):
    def _run_audit(self, root):
        stdout = StringIO()
        stderr = StringIO()
        with override_settings(BASE_DIR=Path(root)):
            call_command(
                "audit_legacy_branding",
                stdout=stdout,
                stderr=stderr,
            )
        return stdout.getvalue(), stderr.getvalue()

    def test_public_source_match_reports_file_line_and_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "templates" / "public.html"
            path.parent.mkdir(parents=True)
            path.write_text("Welcome to AfghanAwaits", encoding="utf-8")

            with self.assertRaises(CommandError):
                self._run_audit(directory)

            stdout = StringIO()
            with override_settings(BASE_DIR=Path(directory)):
                with self.assertRaises(CommandError):
                    call_command("audit_legacy_branding", stdout=stdout)
            self.assertIn("file=templates/public.html:1", stdout.getvalue())
            self.assertIn("term='AfghanAwaits'", stdout.getvalue())

    def test_public_legacy_filename_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "static" / "css" / "afghanawaits.css"
            path.parent.mkdir(parents=True)
            path.write_text("body {}", encoding="utf-8")

            stdout = StringIO()
            with override_settings(BASE_DIR=Path(directory)):
                with self.assertRaises(CommandError):
                    call_command("audit_legacy_branding", stdout=stdout)

            self.assertIn("kind=filename", stdout.getvalue())

    def test_historical_documentation_is_explicitly_allowlisted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "docs" / "relaunch" / "history.md"
            path.parent.mkdir(parents=True)
            path.write_text("Historical AfghanAwaits migration record", encoding="utf-8")

            stdout, _stderr = self._run_audit(directory)

            self.assertIn("audit passed", stdout.lower())

    def test_secret_files_are_never_scanned_or_printed(self):
        with tempfile.TemporaryDirectory() as directory:
            secret = Path(directory) / ".env"
            secret.write_text(
                "TOKEN=do-not-print\nLABEL=AfghanAwaits",
                encoding="utf-8",
            )

            stdout, stderr = self._run_audit(directory)

            self.assertNotIn("do-not-print", stdout + stderr)
            self.assertIn("audit passed", stdout.lower())

    def test_database_match_reports_model_field_id_and_term(self):
        section = ContentSection.objects.create(
            key="legacy-audit-test",
            name="Legacy audit test",
            title="Afghan Awaits",
        )
        with tempfile.TemporaryDirectory() as directory:
            stdout = StringIO()
            with override_settings(BASE_DIR=Path(directory)):
                with self.assertRaises(CommandError):
                    call_command("audit_legacy_branding", stdout=stdout)

        output = stdout.getvalue()
        self.assertIn("model=home.ContentSection", output)
        self.assertIn("field=title", output)
        self.assertIn(f"id={section.pk}", output)
        self.assertIn("term='Afghan Awaits'", output)

    def test_inconsistent_brand_variant_is_a_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "templates" / "variant.html"
            path.parent.mkdir(parents=True)
            path.write_text("Larmoond Trous", encoding="utf-8")

            with self.assertRaises(CommandError):
                self._run_audit(directory)


class LegacyBrandReplacementCommandTests(TestCase):
    def setUp(self):
        self.section = ContentSection.objects.create(
            key="legacy-replacement-test",
            name="Legacy replacement test",
            title="Every Journey Together",
            body="AfghanAwaits trip planning",
        )

    def test_default_mode_is_dry_run_and_shows_exact_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            stdout = StringIO()
            with override_settings(BASE_DIR=Path(directory)):
                call_command("replace_legacy_branding", stdout=stdout)

            self.section.refresh_from_db()
            self.assertEqual(self.section.title, "Every Journey Together")
            self.assertEqual(self.section.body, "AfghanAwaits trip planning")
            self.assertFalse((Path(directory) / "var").exists())
            output = stdout.getvalue()
            self.assertIn('old="Every Journey Together"', output)
            self.assertIn('new="Your Local Host in Afghanistan"', output)
            self.assertIn("Dry run only", output)

    def test_apply_writes_versioned_backup_then_updates_only_approved_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            stdout = StringIO()
            with override_settings(BASE_DIR=Path(directory)):
                call_command(
                    "replace_legacy_branding",
                    apply=True,
                    stdout=stdout,
                )

            self.section.refresh_from_db()
            self.assertEqual(self.section.title, "Your Local Host in Afghanistan")
            self.assertEqual(
                self.section.body,
                "Larmoond Travel and Tours trip planning",
            )
            backups = list(
                (Path(directory) / "var" / "backups" / "legacy-branding").glob(
                    "legacy-branding-*.json"
                )
            )
            self.assertEqual(len(backups), 1)
            payload = json.loads(backups[0].read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(len(payload["changes"]), 2)
            self.assertIn("Applied 2 approved", stdout.getvalue())

    def test_internal_course_identifier_is_not_changed(self):
        from tour.models import TrainingCourse

        course = TrainingCourse.objects.get(code="afghanawaits-onboarding")
        original_code = course.code
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(BASE_DIR=Path(directory)):
                call_command("replace_legacy_branding", apply=True, stdout=StringIO())

        course.refresh_from_db()
        self.assertEqual(course.code, original_code)


class PublicRebrandRenderedPageTests(TestCase):
    def setUp(self):
        Main_things.objects.all().delete()
        Main_things.objects.create(
            hero_description="Plan a requested journey with local coordination.",
            active_public_languages=["en", "fa", "ar"],
        )

    def assertNoProhibitedBranding(self, response):
        body = response.content.decode("utf-8")
        self.assertEqual(list(iter_brand_matches(body)), [])
        self.assertIn("Larmoond Travel and Tours", body)

    def test_home_metadata_and_manifest_use_official_brand(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNoProhibitedBranding(response)
        self.assertContains(response, 'property="og:site_name" content="Larmoond Travel"')
        self.assertContains(response, 'name="twitter:card"')
        self.assertContains(response, 'type="application/ld+json"')

        manifest = self.client.get(reverse("home:site_manifest"))
        self.assertEqual(manifest.json()["name"], "Larmoond Travel and Tours")
        self.assertEqual(manifest.json()["short_name"], "Larmoond Travel")

    def test_account_and_guide_registration_pages_have_no_legacy_brand(self):
        for url_name in ("account_login", "account_signup", "tour:tour_guide_view"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertNoProhibitedBranding(response)

    @override_settings(DEBUG=False)
    def test_404_page_has_no_legacy_brand(self):
        response = self.client.get("/en/definitely-not-a-public-route/")

        self.assertEqual(response.status_code, 404)
        self.assertNoProhibitedBranding(response)

    def test_500_page_has_no_legacy_brand(self):
        request = RequestFactory().get("/en/server-error/")
        request.user = AnonymousUser()
        request.LANGUAGE_CODE = "en"
        SessionMiddleware(lambda _request: None).process_request(request)

        response = custom_500_view(request)

        self.assertEqual(response.status_code, 500)
        self.assertNoProhibitedBranding(response)
