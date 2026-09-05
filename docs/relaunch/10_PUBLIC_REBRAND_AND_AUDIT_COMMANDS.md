# Larmoond Relaunch — Public Rebrand and Audit Commands

**Implementation date:** 2026-08-30
**Official public name:** Larmoond Travel and Tours

## Public-source changes

Task 3 replaces the public legacy identity in active templates, account pages, customer/crew/supplier/operations shells, legal pages, transactional email, Stripe checkout descriptions, translations, JavaScript state, metadata and configured content.

The active head now supplies centralized Open Graph, Twitter and verified-field-only `TravelAgency` JSON-LD metadata. The dynamic manifest continues to use `Main_things`. Error handling includes rebranded 404 and 500 pages.

Legacy-named CSS and JavaScript files were renamed to `larmoond*.css` and `larmoond.js`, and every source reference was updated. The obsolete public `static/brand/afghanawaits/` bundle was removed rather than relabelled. Until exact approved artwork is supplied, templates use configured uploads or the official text wordmark.

There is no existing sitemap implementation or PDF generator/template in this repository, so there were no sitemap display names or generated PDF brand strings to replace. The source auditor includes XML and text templates so either surface will become part of the release gate when implemented.

## Read-only audit command

Run:

```text
python manage.py audit_legacy_branding
```

The command:

- recursively scans text source, templates, PO catalogs, CSS, JavaScript, JSON, XML, fixtures and configuration;
- scans public filenames as well as file contents;
- scans an explicit registry of public/editorial database models and fields;
- introspects physical database columns so it can report safely when migrations are pending;
- reports file and line, or model, field and record ID, plus the matched term;
- never prints matching source lines or database values;
- skips environment, credential, key, media, backup, archive-content and other secret-bearing files;
- never modifies files or data;
- returns a non-zero exit code when a non-allowlisted public occurrence is found;
- also rejects the prohibited misspellings and inconsistent variants listed in the task.

Use `--show-allowlisted` to inspect permitted occurrences:

```text
python manage.py audit_legacy_branding --show-allowlisted
```

The explicit allowlist is in `home/legacy_brand_allowlist.py`. Permitted production-repository categories are limited to legacy hostname/redirect compatibility, historical migration and audit documentation, non-rendered infrastructure identifiers/hotfix archives, and the scanner's own negative-test definitions. A line-specific rule is used for settings and stable identifiers so an unrelated public occurrence in the same file still fails.

## Controlled database replacement command

Dry-run is the default:

```text
python manage.py replace_legacy_branding
python manage.py replace_legacy_branding --dry-run
```

The preview prints the exact model, field, record ID, old value and proposed value. It creates no backup and changes no data.

Apply only after review:

```text
python manage.py replace_legacy_branding --apply
```

Before any update, apply mode writes a versioned JSON export below:

```text
var/backups/legacy-branding/legacy-branding-<UTC timestamp>.json
```

The directory is outside static/media and ignored by Git. Updates run one approved field at a time inside a transaction and require the old value to remain unchanged. A concurrent change aborts and rolls back the transaction while retaining the backup.

The approved registry excludes usernames, emails belonging to accounts, primary keys, internal course codes, file paths, uploads, private notes, notifications, supplier invoices, service orders and all payment history. The implementation never issues a broad SQL string replacement.

## Seed and migration behavior

Historical migration `home.0005` remains unchanged. Reversible migration `home.0008_rebrand_public_content` corrects its four known public `ContentSection` values for new and upgraded databases. The workforce seed now creates the onboarding course with the official title while retaining its stable internal code.

The configured database was updated through the backed-up command, not broad SQL. The backup created during Task 3 is recorded in the completion report and must be retained according to the project's backup policy.

## Release verification

Required release checks:

```text
python manage.py audit_legacy_branding
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --settings=visit_afg_core.test_settings
git diff --check
```

Also inspect the English, Dari and Arabic home/account/error pages, confirmation email, customer dashboard, guide registration, operations and supplier shells, manifest, Open Graph/Twitter tags and JSON-LD. Run a clean controlled `collectstatic`; do not reuse stale collected output.
