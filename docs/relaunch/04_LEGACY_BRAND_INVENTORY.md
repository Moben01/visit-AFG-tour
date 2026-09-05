# Larmoond Relaunch — Legacy Brand Inventory

**Audit date:** 2026-08-29
**Method:** case-insensitive working-tree search for every term requested by the task, followed by a read-only database search over text-like columns. `.git`, `.venv`, binary archives, and collected `staticfiles` were separated from source-code results so vendor/history noise would not be mistaken for a live public reference. The newly written audit documents and `AGENTS.md` necessarily repeat terms as documentation and are not replacement targets.

No branding was changed in this task.

> **Task 3 implementation update (2026-08-30):** Public runtime/source occurrences identified below have now been removed or replaced. The five approved database fields were backed up and updated with `replace_legacy_branding --apply`; `audit_legacy_branding` subsequently passed. This document remains the historical pre-rebrand inventory and is explicitly allowlisted as internal migration documentation.

## Requested exact phrases and contacts

| Search term | Confirmed live/source locations | Required later action |
|---|---|---|
| `AfghanAwaits`, `Afghan Awaits`, `AfghanAwaits.com`, `afghanawaits.com` | Settings/environment defaults; hard-coded legal data; home seed migration; workforce seed signal; Stripe Checkout description; Arabic/Persian PO catalogs; allauth templates; public/RTL/error heads; public headers/footers; home/tour/customer/operations/crew/supplier/destination templates; manifest/SVG titles/brand tokens; CSS/JS names/comments/local-storage key. Detailed file groups below. | Replace public/configured identity in the brand task, while keeping only approved redirect/infrastructure/migration-history uses. Preserve package/app/table names. |
| `Visit Afghanistan Tours` / `Visit Afghanistan` | `templates/footer.html` contains “Why Visit Afghanistan Tours”; policy instructions also contain the prohibited terms. No database match. | Remove/replace the public footer label during rebrand; retain audit/policy text. |
| `info@afghanawaits.com` | `templates/tour/tour-details.html`, `templates/site/footer_v2.html` fallback, `templates/footer.html`, `templates/account/verification_sent.html`; settings also contain a legacy no-reply address. | Replace only with a verified official address; do not invent one. |
| `afghanistan.travel` / `visa-support@afghanistan.travel` | `templates/plan_your_trip/visa_guide.html:591`. | Remove the unsupported contact and do not publish a replacement without operational verification. |
| `Every Journey Together` | `home/migrations/0005_seed_website_sections.py:5`; active database `ContentSection` row `home_map_hero`. | Replace the database-backed content in an approved data migration/content operation during rebrand. |
| `Tours are being prepared` | `templates/site/header_v2.html`, `templates/header.html`, Arabic/Persian PO catalogs. | Replace only when real tour availability/content behavior is approved. Current database has no tours. |
| `No bookable tours are published yet` | `templates/home/home2_v2.html`; Arabic/Persian PO catalogs. | This currently reflects the database truth but is not relaunch copy; replace after publishing real validated tours. |
| `+93 123 456 789` | `templates/things_to_do/New_and_Trending.html:533`; `templates/plan_your_trip/visa_guide.html:604`. | Remove; placeholder number prohibited. |
| `+93 XX XXX XXXX` | `templates/plan_your_trip/Accommodation.html:422-423`. | Remove; placeholder numbers prohibited. |
| `Digital Nomad Program` | `templates/plan_your_trip/visa_guide.html:224`. | Remove/defer unless verified from an authoritative current source; it is not supported by repository capability. |
| `Coastguard` | `templates/plan_your_trip/safety.html:112,120,360`. | Remove; this is copied/stale content inappropriate to inland Afghanistan. |
| `2 hours ago` | `templates/things_to_do/New_and_Trending.html:435`. | Remove dynamic-looking hard-coded freshness claim. |

## Source inventory by layer

### Configuration and runtime strings

- `visit_afg_core/settings.py`: legacy allowed hosts, CSRF origins, deployment-root environment variable, sender, email subject prefix, and production site URL.
- `home/views_v2.py`: English, Persian/Dari, and Arabic privacy, terms, and refund copy naming the legacy brand.
- `tour/views.py`: Stripe Checkout description.
- `tour/signals.py`: `afghanawaits-onboarding` course code/title.
- `home/migrations/0005_seed_website_sections.py`: four seeded legacy brand messages, including “Every Journey Together”.

The old deployment environment variable may need a compatibility period as infrastructure configuration, but it must not leak to public content. Migration files and historical database values should be handled through additive data changes, not edited destructively.

### Public and account templates

Legacy brand identity occurs in:

- `templates/head.html`, `templates/rtl-head.html`, `templates/404.html`;
- `templates/header.html`, `templates/footer.html`;
- `templates/site/head_v2.html`, `header_v2.html`, `footer_v2.html`, `scripts_v2.html`, `scripts_v3.html`;
- `templates/home/home2_v2.html`, `home2_content.html`, `legal_content.html`;
- `templates/tour/tour-details.html`, `tour-booking.html`, `payment.html`, `tourist_dashboard_template.html`;
- `templates/operations/base.html`, `templates/crew/base.html`, `templates/supplier_portal/base.html`;
- `templates/states/province_detail.html`;
- allauth overrides including login, signup, logout, email, email confirmation, password reset/change pages, and verification-sent support text.

The legacy account templates also reference assets under `brand/afghanawaits/` and contain a fixed 2025 copyright in signup.

### Static source assets and client-side state

- Directory `static/brand/afghanawaits/`: manifest, icons, primary/reverse/white logos, monogram, and `brand-tokens.json` all encode the old name.
- `static/css/afghanawaits.css`, `afghanawaits-home2.css`, `afghanawaits-components.css`, `afghanawaits-pages.css`, and `afghanawaits-home-premium.css`: legacy filenames and/or comments.
- `static/js/afghanawaits.js`: legacy filename.
- `static/js/operations-shell.js`: local-storage key `afghanawaits-ops-sidebar`.
- `static/brand/afghanawaits/site.webmanifest`: legacy `name` and `short_name`.
- SVG `<title>` values and alt/ARIA text name the old brand.

Collected `staticfiles/` produced no requested-term match in the scan, which indicates it is stale/different from current source assets. Future deployment must run a clean, controlled `collectstatic`; do not manually edit collected output as the source fix.

### Translation catalogs

Both `home/locale/ar/LC_MESSAGES/django.po` and `home/locale/fa/LC_MESSAGES/django.po` contain the legacy project ID and public strings. The global locale catalogs also contain legacy-theme content. Replacement English source strings must be followed by refreshed translations; replacing only templates would leave legacy copy in catalogs.

## Database-backed legacy inventory

Read-only SQL found:

- Active `ContentSection` title “Every Journey Together”.
- Active content with eyebrow “Why AfghanAwaits”.
- Active section body naming the legacy brand.
- Active professional-section title naming the legacy brand.
- One `TrainingCourse` with a legacy code/title, created by `post_migrate`.
- Two user email identities and one username containing the legacy identity. Values are intentionally omitted because account data must not be exposed in an audit document.

No database match was found for the placeholder phone patterns, `Digital Nomad Program`, `Coastguard`, `2 hours ago`, or the old `Visit Afghanistan` names. No tours are currently published because the tour table is empty.

Account identity changes require a user communication/account-alias plan. They must not be mass-edited by a public-brand data migration without explicit approval.

## Legacy/stale filenames and archives

Root archives named `afghanawaits-*.tar.gz` and `.codex-deploy` hotfix archives are present. Listing archive members showed feature snapshots for home benefits, premium CSS, operations, production settings, trip builder, and tour editor. These are deployment artifacts/history, not runtime source. They may retain the old name only if formally classified as internal migration history; otherwise move them out of the deployable repository in a later housekeeping task.

Legacy-named Python packages, Django app labels, tables, and historical migrations were not renamed and must remain untouched without a separate migration plan, as required by `AGENTS.md`.

## Other placeholder, stale, and unsupported content found

The requested terms revealed a wider copied-content problem:

- `templates/home/home2_content.html` claims a “complete Afghanistan travel system”, vetted drivers, daily route checks, and practical safety delivery. The current database has no tours, bookings, drivers, crew profiles, suppliers, or operating records to substantiate these claims.
- The visa guide presents program/entry information and unsupported support contacts without provenance or review timestamps.
- Safety content includes the irrelevant Coastguard section and other emergency guidance with no cited authority.
- “New and Trending” displays a fake recency timestamp, placeholder hotline, “permitted areas updated weekly”, and theme-style editorial cards.
- Accommodation displays two placeholder institutional phone numbers.
- `tour_involve/tg_dashboard.html` and `tg_doc_newsfeed.html` contain mock operational data, example identities, earnings/charts/invoices/newsfeed content, and dead actions.
- Customer `upcomming_tour_template` advertises fixed counts for Hotels, Flights, Tours, Cars, and Cruise and offers dead “Add” controls. Afghanistan cruise content is copied theme material.
- Many state pages repeat static FAQs, contact panels, raw `.html` links, and unsourced destination claims.
- Legal copy is hard-coded and has no approval/version/effective-date record.

These items should be removed, replaced with verified data-backed content, or deferred; they must not be cosmetically rebranded and published unchanged.

## Rebrand replacement order

1. Approve official operational contacts, legal copy, claims, and real launch content.
2. Secure private storage and stabilize migrations/permissions before inviting users under the new identity.
3. Replace database-backed content and controlled reference data through reviewed, reversible data operations.
4. Replace settings defaults, email sender/subjects, Stripe description, allauth pages, public metadata, headers/footers, and manifests/assets.
5. Refresh translations and verify RTL rendering.
6. Preserve old hostname only in redirects/infrastructure/history; test redirects and canonical URLs.
7. Run the full case-insensitive inventory again against source, rendered pages, database content, built static output, outbound email, PDFs (if added), and deployment configuration.
