# Larmoond Relaunch — Test and Deployment Commands

**Audit date:** 2026-08-29
This document records what exists and what was actually run. It is not authorization to deploy. `AGENTS.md` explicitly prohibits production deployment.

## Existing test runner

The project uses Django's built-in unittest runner:

```powershell
python -B manage.py test --settings=visit_afg_core.test_settings
```

`visit_afg_core/test_settings.py` uses in-memory SQLite, MD5 password hashing, locmem email and dummy Stripe values. There is no pytest/tox/coverage configuration. `requirements.txt` is empty, so the checked-in repository cannot independently reproduce the currently installed virtual environment.

Test distribution at audit time:

| Area | Tests found | Coverage character |
|---|---:|---|
| `accounts` | 8 | Email normalization/uniqueness and allauth/account access. |
| `home` site/content | 12 | Home/destination/content behavior. |
| `home` trip builder | 6 | Request creation/access/proposal flow. |
| `tour` payment/customer | 8 | Booking/payment/customer behavior with mocked Stripe. |
| `tour` operations | 11 | Operations permissions/workflows. |
| `tour` content centre | 10 | Content editing/permission behavior. |
| `tour` resources | 8 | Workforce/supplier/resource workflows. |
| `states`, `things_to_do`, `play_your_trip` | 0 substantive | Test modules are empty or do not test these pages. |
| **Total discovered by runner** | **63** | All passed on SQLite during audit. |

## Commands actually executed and results

All Python commands used `-B` to avoid bytecode writes. No migration, collection, fixture load, seed command, archive extraction, deployment, or production-data mutation was run.

### Django system check

```powershell
python -B manage.py check
```

Result: exit 0 — `System check identified no issues (0 silenced).`

### Deployment-oriented Django check

```powershell
python -B manage.py check --deploy
```

Result: exit 0 with three warnings:

- `security.W004`: `SECURE_HSTS_SECONDS` is unset.
- `security.W008`: `SECURE_SSL_REDIRECT` is not true; an upstream redirect is assumed but not versioned here.
- `security.W009`: the fallback `SECRET_KEY` is insecure.

### Migration drift check

```powershell
python -B manage.py makemigrations --check --dry-run
```

Result: exit 0 — `No changes detected.`

Important qualification: this does **not** validate reproducibility. Apps without migration modules are treated as unmigrated, and the source tree lacks the migration histories recorded in PostgreSQL. Only the untracked `home/migrations` exists. A clean-database and production-copy migration rehearsal remains mandatory.

### Test suite

```powershell
python -B manage.py test --settings=visit_afg_core.test_settings
```

Result: exit 0 — 63 tests found, 63 passed in 6.704 seconds, test database created/destroyed. One debug print, `req is not htmx`, appeared and should eventually be removed from test/runtime output.

### Source/diff integrity

The final audit validation command is:

```powershell
git diff --check
```

Result: exit 0 — no whitespace errors. Git emitted line-ending conversion warnings for pre-existing modified working-tree files. Because the repository was already dirty and the audit files are untracked, the eight documents were also enumerated individually and scanned; no trailing whitespace was found in them.

## Read-only audit commands used

The repository was inspected with read-only PowerShell/Git/ripgrep commands, chiefly:

```powershell
Get-Content -LiteralPath AGENTS.md
git status --short --branch
rg --files
rg -n -i "<audit patterns>"
Get-ChildItem -Recurse
python -B manage.py showmigrations
```

Database inspection used Django/PostgreSQL only after setting the connection transaction to `default_transaction_read_only = on`. Queries were limited to schema metadata, migration ledger rows, aggregate counts, route/content strings, indexes and legacy-term existence. No sensitive row values or file contents were emitted.

Archive inspection listed members only; no archive was extracted. Local source images/media were inventoried by path only unless needed to establish their public/private role.

## Commands that must not be treated as safe audit checks

The following can write data/files and were deliberately not run:

```powershell
python manage.py migrate
python manage.py migrate --run-syncdb
python manage.py makemigrations
python manage.py collectstatic
python manage.py loaddata <fixture>
python manage.py enforce_email_identity
```

- `migrate` triggers `tour.signals.seed_resource_reference_data`, which writes roles, supplier categories and training courses.
- `migrate --run-syncdb` can create tables outside a migration history.
- `enforce_email_identity` mutates user/allauth rows and invokes `schema_editor` for a constraint.
- `collectstatic` writes built assets and may overwrite/duplicate the existing stale `staticfiles` tree.

These commands require an approved implementation/deployment task, backups where applicable, a verified target settings module, and a reviewed migration/runbook.

## Existing deployment configuration

There is no authoritative deployment configuration in the repository:

- no Dockerfile/Compose, Procfile, platform manifest, CI workflow, systemd unit, Nginx config, health check, or release script;
- no populated dependency manifest or lock file;
- comments in settings refer to systemd environment, Nginx TLS and Gunicorn, and an environment-selected shared app root;
- root and `.codex-deploy` tarballs are manual feature/hotfix snapshots;
- production static/media behavior is therefore partly assumed and cannot be verified from versioned files.

No production command was executed.

## Required verification sequence for future implementation tasks

After the schema baseline and dependency manifest are approved, a safe CI/staging sequence should be designed around:

```powershell
python -B manage.py check --settings=<staging-settings>
python -B manage.py check --deploy --settings=<staging-settings>
python -B manage.py makemigrations --check --dry-run
python -B manage.py test --settings=visit_afg_core.test_settings
python -B manage.py test --settings=<postgres-test-settings>
git diff --check
```

Then, in an isolated disposable/staging environment only:

1. Install from a pinned, reviewed dependency set.
2. Create a clean PostgreSQL database from migrations and run system checks.
3. Restore a sanitized production-like copy and rehearse the upgrade with backups and rollback timing.
4. Build static assets into a clean artifact directory and crawl/review rendered pages.
5. Verify anonymous denial and authorized access for every private media type.
6. Run Stripe test-mode webhook mismatch/replay/idempotency cases.
7. Validate email sender/reply-to, translated templates and failure handling without real customer data.
8. Smoke-test canonical redirects, sitemap/robots/noindex, login, trip request, quote, booking, payment, documents, pickup, crew and supplier journeys.

The exact migrate/collectstatic/service restart commands must be supplied by a later approved deployment runbook. They cannot be inferred safely from the current repository.

## Manual verification checklist for the relaunch program

- Public desktop/mobile/RTL header, footer, focus order, keyboard navigation and contrast.
- Every named route plus preserved legacy redirects; no raw `.html`, `#`, or `javascript:void(0)` customer action.
- Role matrix for anonymous, unverified, Tourist, unapproved/approved crew, supplier, Operator, content editor, Moderator, staff and superuser.
- Direct/guessed private-document URLs fail for all unauthorized users and do not leak through logs/cache/referrer.
- Booking owner can see only their booking, quote, itinerary, required documents, pickup and welcome package.
- Operations users see only permissions assigned to their job; finance/document/content privileges remain separate.
- Stripe test payments reconcile correct amount/currency/reference; duplicates and mismatch fail safely.
- Only real approved tours, prices, contacts, capabilities and verified reviews are visible.
- Metadata/canonical/Open Graph/JSON-LD/sitemap/robots/manifest reflect the approved Larmoond identity and never expose private pages.
- Backup restore and rollback are timed and documented before any production change.
