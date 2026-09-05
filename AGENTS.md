# AGENTS.md — Larmoond Travel and Tours

## Product Mission

This repository powers the public website, trip planning, quotation,
booking, traveller coordination, and tour operations of
Larmoond Travel and Tours.

The website must present Larmoond as a real Afghan travel operator and
local host, not only as an information portal.

## Official Brand

Official English name:
Larmoond Travel and Tours

Short public name:
Larmoond Travel

Dari name:
لارموند تراول و تور

Primary brand message:
Your Local Host in Afghanistan

Primary hero message:
Afghanistan, hosted by those who call it home.

Official colors:
- Deep Green: #072720
- Lime Green: #9EDD05
- White: #FFFFFF

## Legacy Branding

The following names must not appear in public-facing content:

- AfghanAwaits
- Afghan Awaits
- AfghanAwaits.com
- Visit Afghanistan Tours
- Visit Afghanistan
- info@afghanawaits.com
- visa-support@afghanistan.travel

The old hostname may remain only in:
- redirect configuration;
- infrastructure records;
- historical migrations;
- internal migration documentation.

Do not rename Python packages, database tables, or Django app labels
during the public rebrand unless a separate approved migration plan exists.

## Non-Negotiable Rules

1. Inspect existing code before changing it.
2. Reuse or extend existing models instead of creating duplicates.
3. Preserve existing data and working URLs.
4. Prefer additive and reversible migrations.
5. Never delete production data automatically.
6. Never use placeholder telephone numbers, emails, addresses, prices,
   reviews, statistics, licence details, or travel claims.
7. Never invent visa, security, legal, weather, or entry information.
8. Never publish fake testimonials or fake completed tours.
9. Do not expose passports, identity documents, traveller documents,
   guide documents, internal prices, or supplier details publicly.
10. Do not store card information.
11. Do not deploy to production.
12. Do not modify unrelated applications or formatting.
13. Follow the repository's existing architecture and coding conventions.
14. Add tests for every business workflow and permission boundary.
15. All user-facing English must be professional and natural.
16. Brand names must not be translated or misspelled.
17. Public claims must be supported by real operational capability.

## Data Protection

- Collect passport information only after a booking is confirmed.
- Private documents must not be stored under publicly accessible media URLs.
- All private file downloads require authorization.
- Sensitive identifiers must not appear in logs, URLs, analytics, or emails.
- Staff permissions must follow least privilege.
- Customer data must never be used in fixtures or screenshots.

## Required Workflow

For every task:

1. Read this AGENTS.md.
2. Inspect the relevant models, views, URLs, templates, services, forms,
   settings, translations, tests, and existing data structures.
3. Produce a short implementation plan.
4. Identify risks and migrations.
5. Implement only the approved scope.
6. Add or update tests.
7. Run the appropriate checks.
8. Review the final diff.
9. Report all changes.

## Required Completion Report

At the end of every task, report:

- Summary of implementation
- Files created
- Files modified
- Database migrations
- Tests added or updated
- Commands executed
- Test results
- Manual verification steps
- Remaining risks
- Suggested Git commit message

## Verification

Use the existing project test runner.

At minimum, when applicable, run:

- python manage.py check
- python manage.py makemigrations --check --dry-run
- python manage.py test
- git diff --check

Never claim that a task is complete without showing test results.