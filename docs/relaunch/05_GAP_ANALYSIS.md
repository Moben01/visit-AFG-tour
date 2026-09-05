# Larmoond Relaunch — Gap Analysis

**Audit date:** 2026-08-29
This compares the current working tree to the product mission and non-negotiable rules in `AGENTS.md`. Priority is **P0** (must block launch), **P1** (must be completed for launch readiness), **P2** (important improvement), or **P3** (defer unless launch scope requires it).

## Security, privacy, and permissions

| Priority | Current state | Gap / required outcome | Reuse direction |
|---|---|---|---|
| P0 | One public media storage/root serves editorial and sensitive files. Templates link private documents using direct `.url`. | Separate private storage paths/backends; authenticated object-level download endpoints; no public media URL for passports, visas, IDs, CVs, contracts, invoices, certificates, receipts or traveller records; define retention and access logging. | Keep existing file fields where possible and change storage/download behavior additively. |
| P0 | Public tour detail renders every `EnquireUs.full_name`, message, and date with fake social counts. | Treat enquiries as private leads. Remove public rendering; restrict operations view; add consent, response state, retention and tests. | Reuse `EnquireUs`; do not create a testimonial from these records. |
| P0 | Operations authorization combines staff/superuser and string roles; one broad decorator admits users to documents, bookings and customers. | Define permission matrix and least-privilege groups/permissions; separate booking, finance, content, identity-document, workforce and supplier duties. | Extend Django permissions and current decorators/mixins. |
| P0 | Public guide/translator forms collect identity/CV data into public media; validation is incomplete. | Disable or replace with authenticated crew onboarding after secure storage, file type/size/malware policy, consent and access controls. | Reuse `CrewMember`, `CrewQualification`, and `CrewDocument`. |
| P1 | Crew/supplier portal access is based on profile existence; any authenticated user can self-create either profile; approval is not a universal gate. | Explicit onboarding/approval states and role policy; prevent unapproved profiles from seeing operational data. | Extend current profiles/status fields. |
| P1 | Crew can open non-public opportunity detail by guessed ID. | Filter portal detail to open/published opportunities or the user's own related application/offer. | Fix existing view/queryset. |
| P1 | Supplier order actions accept transitions without checking the current state graph. | Enforce allowed transitions atomically and audit who changed state. | Extend existing `ServiceOrder`. |
| P1 | Trip ownership uses scalar IDs and session UUIDs. | Preserve public UUID flow but add secure real relationships, expiry/rate limiting, audit, and clear anonymous recovery rules. | Extend existing trip request models. |

## Schema and data governance

| Priority | Current state | Gap / required outcome | Reuse direction |
|---|---|---|---|
| P0 | Live migration ledger has histories not present in source; most local apps are unmigrated/syncdb; home migrations are untracked. | Establish a source-controlled baseline that matches every target database. Rehearse fake-in/baseline and rollback on database copies before any schema feature. | Preserve all current tables/app labels; no rename/rebuild. |
| P0 | `post_migrate` silently seeds mutable reference/training data. | Move deterministic reference changes to reviewed data migrations or explicit idempotent management command; prevent reintroducing legacy strings. | Reuse current records/codes with a mapping plan. |
| P0 | `enforce_email_identity` edits data and creates a constraint through a management command. | Represent schema constraints in migrations and keep data normalization separate/rehearsed. | Preserve existing email constraint and identities. |
| P1 | Two pre-arrival models collect overlapping sensitive information. | Select one canonical aggregate, map every field/status/file, migrate additively, and retain compatibility until verified. | Extend, do not add a third workflow. |
| P1 | Legacy provider models overlap the fuller crew system. | Bridge legacy guide/translator/security records and tour assignments into crew roles/engagements; remove only after reconciliation. | Canonicalize on current crew models. |
| P1 | Static province pages, `ProvincePage`, `PopularPlace`, and four things-to-do models overlap. | One managed destination/content workflow with compatibility routes and staged content migration. | Extend `ProvincePage` and content sections/items. |
| P1 | Favourite/user-itinerary/itinerary/ready-booking cardinality is under-constrained or wrong. | Add reviewed uniqueness/order constraints after duplicate audit; correct intended cardinality. | Additive migrations only after baseline. |
| P2 | Operational filters lack targeted composite indexes. | Capture production-like query plans and add indexes for booking, enquiry, crew, supplier, RFQ/order/invoice, itinerary and trip-ownership queues. | Index existing models. |
| P2 | Statuses, currencies and amounts are inconsistent/free-form; payment amount can lose cents. | Normalize choices, decimal/currency semantics and transition rules without losing historical values. | Extend existing columns/models via compatibility fields. |

## Tours, quotations, bookings, and payments

| Priority | Current state | Gap / required outcome | Reuse direction |
|---|---|---|---|
| P0 | Stripe webhook verifies signature but does not conclusively compare amount/currency/reference with the server-side expected booking before paid state. | Verify event/session identity, amount, currency, booking reference and livemode; implement idempotent transaction/audit; reject mismatch. | Harden existing Stripe Checkout integration; no card storage. |
| P1 | Tour absolute URL reverses the wrong route; category view can 500 and filter semantics are incorrect. | Repair route reverse and 404/query handling; cover with tests. | Fix existing views/model method. |
| P1 | `PickupPlan` status view calls nonexistent `mark_picked_up`; pickup permissions exclude role-based Operators. | Implement/test status transition method and align permission policy. | Fix existing pickup workflow. |
| P1 | Welcome-package template depends on unmounted admin; pickup template has an invalid unnamespaced reverse. | Route all actions through mounted application views and named namespaces. | Reuse existing operations/customer views. |
| P1 | `TourGuideAssignment` lacks a guide; direct Tour provider FKs conflict with crew engagements. | Use `CrewEngagement` as canonical assignment with a compatibility display/query layer. | Extend current resource network. |
| P1 | Customer itinerary edits copy full records and can choose global resources. | Restrict eligible resources, establish versioning/price re-quote rules, and consider delta overrides. | Reuse itinerary and user customization workflow. |
| P2 | No custom PDF quote/itinerary/booking artifact; export is CSV only. | Build only if operations require a verified customer document; private delivery, immutable snapshot and tests required. | Derive from proposal/booking/itinerary data. |
| P2 | Enquiry capture has no dedicated notification/service workflow. | Add private operations notification/assignment/response workflow after official email/contact approval. | Extend `EnquireUs`. |

## Public experience, content, and brand readiness

| Priority | Current state | Gap / required outcome | Reuse direction |
|---|---|---|---|
| P0 | Legacy identity occurs in settings, database, templates, translations, assets, emails and payment description. | Execute coordinated public rebrand only after verified contacts/content/redirect plan; old hostname only in permitted internal/redirect contexts. | Replace surfaces; preserve internal app/table labels. |
| P0 | Visa, safety, entry, weather and legal pages contain unsourced/copy-pasted claims and placeholder contacts. | Remove/defer unverified claims; introduce owner, source, reviewed-at/effective date and approval workflow. Legal copy requires qualified approval. | Use managed content; do not invent replacements. |
| P0 | Home content claims vetted drivers/daily route checks/complete delivery without supporting operating records. | Publish only claims backed by documented real capability. | Make claims database/config controlled and approved. |
| P1 | Navigation differs across public, legacy, customer, operations, crew and supplier pages; raw HTML/dead links are common. | One role-aware named-URL navigation system; preserve URLs through redirects; eliminate dead actions. | Extend new header/footer and portal shells. |
| P1 | Customer detail pages embed a legacy travel-agent theme with Hotels/Flights/Cruise and fabricated counts. | Remove mock widgets and display only real booking itinerary, payment, pre-arrival, pickup and support data. | Reuse customer/booking records. |
| P1 | URL naming/casing is inconsistent and duplicated. | Define canonical lowercase hyphenated routes; keep named aliases/301 redirects and validate reverse compatibility. | Preserve working external URLs during transition. |
| P1 | Dynamic province model has no rows while 37 static routes carry stale content. | Curate/approve real destination pages before switching routes. | Populate `ProvincePage`, do not create another destination app. |
| P1 | There are no bookable tours/content records in the current database. | Launch content must be real, operationally supportable, priced/availability-approved, and tested. | Populate existing Tour/Category/Itinerary models through content centre. |
| P2 | Account settings refers to nonexistent profile attributes and does not update data. | Align form/template with `CustomUser` and explicit profile models; validate ownership and uploads. | Extend current account page. |
| P2 | Arabic/Persian catalogs exist; Pashto does not; legacy strings remain. | Confirm launch languages, professional translations and terminology; refresh catalogs and RTL QA. | Reuse i18n structure. |
| P2 | Unused templates and copied theme/vendor assets remain. | Remove only after runtime/reference/static-build audit and recovery plan; do not mix cleanup with core workflow changes. | Prefer staged removal. |

## SEO, metadata, and discoverability

| Priority | Current state | Gap / required outcome |
|---|---|---|
| P1 | No sitemap or `robots.txt`; no canonical, Open Graph, Twitter card or JSON-LD. | Add per-page canonical/localized metadata, sitemap and robots behavior after canonical routes/domain are approved. Use real Organization/Tour data only. |
| P1 | Generic global description/title and `index,follow` apply broadly. | Per-page metadata and intentional indexing; keep all private/operations/customer/crew/supplier/auth pages noindex. Operations already uses noindex but other private shells need verification. |
| P1 | Manifest and icons name the legacy brand. | Replace manifest/icons/colors/install metadata in coordinated rebrand and test PWA cache/update behavior. |
| P2 | Mixed-case/duplicate URLs split canonical signals. | Redirect to a single lowercase canonical form while preserving old links. |

## Email, PDF, services, and operational integration

| Priority | Current state | Gap / required outcome |
|---|---|---|
| P1 | SMTP/allauth only; no verified official contact/address, enquiry, booking, proposal, document or operations email service. | Confirm official sender/reply-to and build explicit, tested transactional events with privacy-safe content and failure handling. |
| P1 | No service layer; payment and workflow logic is embedded in large views. | Extract narrowly scoped transactional services as workflows are hardened; do not rewrite wholesale. |
| P2 | No PDF generation. | Build only approved quote/itinerary/booking PDFs, with private storage or on-demand authorized streaming and visual tests. |
| P2 | No background job/queue or retry mechanism. | Determine whether email/PDF/webhook follow-ups need a queue; defer new infrastructure until an operational requirement exists. |

## Tests and quality controls

Current suite: 63 Django unittest tests; all pass on in-memory SQLite. `states/tests.py`, `things_to_do/tests.py`, and `play_your_trip/tests.py` contain no substantive tests. There is no coverage configuration/report.

Missing high-value tests:

- authorization and direct-download denial for every private document type;
- public tour detail must never expose enquiry PII;
- public upload authentication, file extension/MIME/size policy and rejected documents;
- Stripe webhook wrong amount/currency/reference, duplicate delivery, stale session, wrong mode and transaction rollback;
- `Tour.get_absolute_url`, missing category, invalid filters, namespaced pickup/admin reverses and all canonical redirects;
- pickup status transitions and the missing-method branch;
- crew draft-opportunity visibility and profile approval gates;
- supplier order transition graph and ownership boundaries;
- favourites/user itinerary/ready-booking duplicate constraints;
- PostgreSQL-specific constraints, indexes, case-insensitive email, JSON and transaction behavior;
- migration baseline from empty database and upgrade rehearsal from a production-like copy;
- `post_migrate` seed idempotency/legacy replacement and the email management command;
- legal/content approval, metadata, sitemap, robots, manifest and noindex behavior;
- i18n/RTL, accessibility, HTMX/JavaScript and critical browser journeys;
- deployment/static/media/email configuration smoke checks.

## Deployment and operations

| Priority | Current state | Gap / required outcome |
|---|---|---|
| P0 | No Dockerfile, Procfile, systemd, Nginx, platform manifest, CI/CD, health check or reproducible dependency manifest. | Document and version the actual deployment path without deploying; pin dependencies; add check/test/static/migration gates and rollback/runbook. |
| P0 | Production comments assume Gunicorn/Nginx/systemd and a shared directory, but no config proves TLS redirect or media protection. | Add reviewed infrastructure configuration or external runbook; verify HTTPS, host/proxy settings, private media denial, backups and restore. |
| P1 | Root hotfix tarballs and `.codex-deploy` archives represent manual release fragments. | Inventory and retain only controlled history; do not treat archives as deploy source. |
| P1 | `check --deploy` warns about HSTS, SSL redirect and fallback key. | Resolve at Django or documented proxy layer; remove insecure production fallbacks; stage HSTS safely. |
| P1 | No observability/error reporting/audit log/backup proof in repository. | Define privacy-safe application logging, error monitoring, security/audit events, database/media backup and restore tests. |

## What must be reused instead of rebuilt

1. `Tour`, `TourCategory`, `ItineraryItem`, `Booking`, existing Stripe Checkout, customer booking pages, pickup and welcome-package models.
2. `TripRequest`, stops/preferences, route proposals/days, operations proposal handling and booking conversion.
3. `CrewMember` through `CrewEngagement`, training/cases/notifications, instead of new guide/translator/host tables.
4. `ServiceSupplier` through RFQ/quote/order/invoice/review, instead of a new supplier platform.
5. `ContentSection`/`ContentItem`, `ProvincePage`/sections, `PopularPlace`, `ManagedMedia`, and the operations content centre.
6. Current allauth email-first authentication and mandatory verification.
7. Current role-specific dashboards as shells, after permission and navigation repair.

The correct relaunch architecture is a hardened, consolidated version of what exists, with compatibility migrations and redirects—not a parallel replacement stack.
