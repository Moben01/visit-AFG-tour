# Larmoond Relaunch — Current-State Audit

**Audit date:** 2026-08-29
**Scope:** read-only review of the current working tree and the configured local PostgreSQL database
**Repository state:** `main` is three commits ahead of `origin/main` and already contains many modified and untracked user files. Those pre-existing changes were treated as part of the state being audited and were not altered.

## Executive assessment

This is a working Django 5.2 application with more operational capability than the public site suggests. It already contains tours and itineraries, enquiries, bookings, Stripe Checkout, a trip-request/quotation workflow, customer trip coordination, workforce/crew management, supplier procurement, an operations dashboard, and a database-backed content centre. These capabilities should be repaired and extended rather than recreated.

The relaunch is not ready for a public brand switch. The critical blockers are:

1. Sensitive guide, crew, supplier, passport, visa, insurance, flight, contract, invoice, and payment-receipt files share the public `MEDIA_URL`/`MEDIA_ROOT` design and are linked by direct `.url` values. There is no authorization-gated download service.
2. Source-controlled schema history is not reproducible. Only an untracked `home/migrations/` directory is present; the live database records migration histories for `accounts`, `tour`, and `things_to_do` that are absent from this tree, while `tour/signals.py` explicitly assumes `migrate --run-syncdb`.
3. The public tour detail exposes every enquiry sender's full name and message as a review-style feed. Enquiries are not testimonials and may contain private information.
4. Permissions are broad and role handling is split between a string field, Django staff/superuser flags, Django permissions, and portal-profile existence. Least privilege is not consistently enforced.
5. The public experience mixes a newer database-backed shell with large, copied legacy destination/planning pages, mock dashboards, raw `.html` links, mixed-case URLs, placeholder contacts, unsupported claims, and legacy branding.
6. There is no repository deployment definition, no production web-server/private-media configuration, no CI, no dependency lock or populated `requirements.txt`, no sitemap or `robots.txt`, and no structured metadata.

## 1. Project structure

| Area | Purpose and present state |
|---|---|
| `visit_afg_core/` | Project settings, root URL configuration, WSGI and ASGI entry points. |
| `accounts/` | Custom email-based user model and one account-settings page. |
| `home/` | Home/search, legal pages, favourites bridge, content models, destinations, trip builder, route proposals, and content management support. |
| `tour/` | Core tour/booking/itinerary/payment models and views; customer portal; operations; crew/workforce; supplier/procurement; content editor. This is the main business application. |
| `states/` | Static province routes/templates plus one newer dynamic `ProvincePage` renderer. No models. |
| `things_to_do/` | Four parallel content model families and static experience pages. |
| `play_your_trip/` | Static visa, safety, accommodation, transport, weather, currency, accessibility, and attractions-pass pages. No models. |
| `templates/` | Public site, RTL, allauth overrides, operations, crew, supplier, customer, legacy agent, destination, and trip-planning templates. |
| `static/` | Source assets plus a large copied theme/vendor estate and legacy-named brand/CSS/JS assets. |
| `staticfiles/` | Collected output checked into or left in the working tree; it does not reflect all current source matches and must not be treated as the source of truth. |
| `locale/`, `home/locale/` | Arabic (`ar`) and Persian/Dari (`fa`) PO catalogs. |
| `.codex-deploy/`, root `*.tar.gz` | Ad-hoc feature/hotfix archives, not a reproducible deployment system. |

Installed first-party apps are `accounts`, `home`, `tour`, `states`, `things_to_do`, and `play_your_trip`. Installed third-party components are `django-allauth`, `django-htmx`, `django-jazzmin`, `django-rosetta`, `django-multiselectfield`, Stripe, Pillow, and PostgreSQL support. `requirements.txt` is empty and no `pyproject.toml`, lock file, tox, pytest, or coverage configuration exists.

## 2. Settings and environment

Primary evidence: `visit_afg_core/settings.py`, `visit_afg_core/test_settings.py`, `visit_afg_core/urls.py`.

- Production-style defaults target PostgreSQL (`visitafgtoursdb`, user `postgres`, password fallback `root`, host `localhost`). Credentials can be supplied through environment variables, but insecure local fallbacks exist.
- `SECRET_KEY` has an insecure fallback. `DEBUG` defaults false.
- `ALLOWED_HOSTS`, CSRF trusted origins, site domain, and default sender use the legacy hostname/address by default.
- SMTP is environment-driven; absent credentials fall back to the console backend. No application-specific outbound email service was found beyond allauth.
- Authentication is email-first, username is disabled for allauth, email is required and verification is mandatory.
- `AUTH_USER_MODEL = accounts.CustomUser`.
- `TIME_ZONE = "UTC"`, not the operating timezone named in the repository context. This may be intentional for storage, but display/operations behavior must be verified.
- `STATIC_ROOT` and `MEDIA_ROOT` use local directories or an environment-selected shared deployment root whose variable is still legacy-named.
- Secure cookies and proxy SSL header support are set, but `check --deploy` reports no HSTS, no Django `SECURE_SSL_REDIRECT`, and an insecure fallback key. An upstream redirect is assumed but no upstream config is in the repository.
- `i18n_patterns` prefixes English as `/en/`. The configured languages are English, Persian, and Arabic; there is no Pashto locale. Some comments call `fa` Dari while other content is generic Persian.
- The root project does not mount Django admin. Jazzmin/admin registrations therefore have no reachable admin route in this URL configuration.
- `test_settings.py` uses in-memory SQLite, MD5 password hashing, a locmem email backend, and dummy Stripe credentials. Its comment says local app migrations are disabled, but `MIGRATION_MODULES` only disables selected contrib/allauth-related apps.

## 3. Authentication, roles, and permissions

`CustomUser` extends `AbstractUser`, normalizes email, makes email unique, and adds a case-insensitive database uniqueness constraint. Its role field is named `my_choice_field` with `Tourist`, `Guide`, `Translator`, `Operator`, and `Moderator` values.

The effective authorization system is fragmented:

- allauth controls sign-up/sign-in and mandatory email verification;
- `is_staff` and `is_superuser` control parts of the application;
- `my_choice_field` controls operations access;
- one content permission checks `home.change_contentsection`;
- crew and supplier access is granted by the existence of a related `CrewMember` or `ServiceSupplier` profile;
- any authenticated user can start crew or supplier onboarding, regardless of the declared account role.

`operations_required` admits any staff user, superuser, Operator, or Moderator to bookings, customers, document queues, providers, reports, and resources. Only selected actions, such as manual crew/offline-payment operations, narrow this further. Content editing instead admits superusers, Moderators, or users with one Django permission and excludes Operators by default. Pickup edit/status views require `is_staff`, even though role-based Operators can reach the operations portal. This is inconsistent and too coarse for traveller/identity documents.

Customer booking and pre-arrival views generally scope records to the signed-in owner (staff can override), and passport data is requested only after a paid booking in those views. Trip requests allow the signed-in scalar owner or a browser session holding the request UUID. These are reusable foundations, but explicit object permissions and document download authorization are still required.

## 4. Existing business workflows

| Workflow | Current capability | Audit assessment |
|---|---|---|
| Tours/catalogue | Categories, tours, images, includes/excludes, FAQs, itinerary days, availability and price-on-request. | Reuse; fix routing, publishing rules, validation, duplicated resources, metadata, and tests. |
| Search/favourites | Home search across tours/destinations and user favourites. | Reuse; add uniqueness and POST-only mutation. |
| Trip planning/quotation | Public trip builder, ordered stops/preferences, operations review, proposals/days, send/accept/reject, and booking conversion. | Strong reusable workflow; scalar user/staff/booking identifiers should become safe relationships through an additive migration plan. |
| Booking | Traveller details/counts, status, payments, customer list/detail, CSV export, operations management. | Reuse; normalize status/payment fields and add indexes/constraints. |
| Payment | Server-side quote calculation, Stripe Checkout, success/cancel, signed webhook, manual payment record. No card fields are stored. | Reuse, but verify webhook amount/currency/reference and idempotency; stop integer/cents loss and legacy statement text. |
| Pre-arrival | Two parallel document models and forms; passport/visa/insurance/flight/emergency/medical data. | Consolidate by extending one model after a data-preserving bridge. Secure storage first. |
| Pickup/welcome | Driver/operator/vehicle, pickup plan/status/proof, gifts and welcome package. | Reuse; `picked_up` calls a missing model method, permissions conflict, and admin links are unreachable. |
| Crew/workforce | Profiles, roles, qualifications, documents, availability, opportunities, applications, offers, engagements, payments, reviews, training, cases, notifications. | Prefer this newer workflow over legacy Guide/Translator/SecurityGuard assignment models. Fix draft visibility and verification/approval gates. |
| Suppliers/procurement | Profiles, categories, documents, services/assets/contracts/rates, requirements, RFQs, quotes, orders, invoices, reviews. | Reuse and extend; enforce state transitions and document privacy. |
| Content/destinations | Sections/items, popular places, province pages/sections, media library, four things-to-do families, tour editor and operations content centre. | Reuse a consolidated content model; retire duplicated static and four-model publishing paths only after URL/data compatibility. |
| Enquiries | Tour-scoped enquiry capture and admin/operations visibility. | Must stop rendering enquiries publicly. Add privacy, consent, workflow state, and notification handling. |

There are no dedicated `services.py` modules. Business logic is concentrated in views, models, forms, decorators, and `post_migrate` signals. This makes transaction boundaries and external integration behavior harder to test.

## 5. Public content, templates, assets, and metadata

- The current home shell is database-backed and includes dynamic destinations/tours, search, trip builder, service bridge, header/footer, currency, and legal pages.
- Large portions of `states/`, `things_to_do/`, `play_your_trip/`, and `tour_involve/` remain copied theme pages with raw `.html` links, `href="#"`, fabricated-looking counters, demo users, static news timestamps, and irrelevant travel categories.
- Customer navigation is inconsistent: the modern customer overview leads into legacy `upcomming_tour_template` and agent-dashboard markup with dead “add hotel/flight/tour/car/cruise” controls.
- The global header sends every authenticated role to “My bookings”; operators, crew, and suppliers instead need role-appropriate navigation. “Become an expert” still uses the legacy unauthenticated guide form rather than the crew workflow.
- The public enquiry partial renders `full_name`, message, date, fixed like/dislike/heart counts, and a nonfunctional Reply action for every enquiry on the tour detail page.
- Global metadata is limited to a generic title/description and `robots=index,follow`; there is no canonical URL, Open Graph, Twitter card, JSON-LD, sitemap, or `robots.txt` route.
- `manifest.json`, logo/brand paths, CSS and JS filenames/comments, local-storage keys, translation catalogs, and third-party descriptions still contain the legacy identity.
- A SweetAlert script is loaded from jsDelivr inside the enquiry partial; other CDN/theme dependencies are mixed with local vendor assets. No Content Security Policy was found.
- No PDF generation exists. Booking export is CSV only.
- No fixtures were found. The only management command, `accounts/management/commands/enforce_email_identity.py`, mutates user/allauth data and adds a database constraint via `schema_editor`, outside a normal migration.
- `tour.signals.seed_resource_reference_data` writes 13 crew roles, 13 supplier categories, and two training courses after every migration. One course contains legacy code/title. Reference data should be migration- or command-governed, not silently written by startup migration signals.

## 6. Data and storage audit

The configured PostgreSQL 16.1 database was queried after `SET default_transaction_read_only = on`; only schema metadata, aggregates, public content, and legacy-term matches were inspected. No identity-document contents or customer PII values were printed.

Current aggregate state:

- 3 users: 2 Tourist and 1 Moderator. Legacy identity strings occur in two email values and one username; those values are intentionally omitted from this report.
- 10 active `ContentSection` rows, 9 active `ContentItem` rows, and 8 active `PopularPlace` rows.
- 0 `ProvincePage`, `ManagedMedia`, trip request/proposal, tour, category, booking, itinerary, accommodation, transport, guide, translator, security, enquiry, or things-to-do business rows.
- 13 `CrewRole`, 13 `SupplierCategory`, and 2 `TrainingCourse` reference rows; all other newer workforce and supplier tables are empty.
- No database file-field record was found and no mixed-case slug value was present in existing slug columns.

Database-backed legacy content remains in active sections (“Every Journey Together”, “Why AfghanAwaits”, and two other AfghanAwaits references), one seeded training course, and account identities. Eight destination rows point to a mix of lowercase and mixed-case legacy route names (`states:kabul`, `states:Herat`, `states:Nangarhar`, and similar).

All `FileField` and `ImageField` values use the single default storage. Direct `.url` links are rendered for passport, visa, insurance, invitation, flight ticket, crew, supplier, contract, invoice, voucher, certificate, qualification, receipt, and other files. Development serves `/media/` directly; production behavior depends on absent reverse-proxy configuration. The design therefore cannot meet the private-document rules even though the current database happens to contain no uploaded file records.

## 7. Defects and stale behavior confirmed during audit

- `Tour.get_absolute_url()` reverses `tour_detail`, but the route is named `tour:tour_details`.
- `pickup_update_status` calls `PickupPlan.mark_picked_up()`, which does not exist.
- `translator_view` uses a `TranslatorForm` whose initializer is misspelled `_init_`; required model fields are excluded and the public form has no upload security policy.
- The public guide application captures ID/passport identifiers and a CV into public media without authentication or least-privilege download controls.
- `toggle_favorite` changes state via GET and the model lacks a user/tour uniqueness constraint.
- `TourGuideAssignment` has no guide relationship.
- `Ready_tour_for_booking` is unique by user alone, preventing more than one row per user across all tours.
- `tour_category_list` uses `.get()` rather than 404 handling and replaces category filtering with raw category IDs for a `types` parameter.
- Customer itinerary customization can select global accommodation/transport records and lacks uniqueness for repeated user/item copies.
- Stripe success checks metadata/payment status and the webhook signature, but payment completion is not tied to an independently verified expected amount/currency/reference before setting paid. Amount handling mixes decimal dollars and integer values.
- Crew opportunity detail does not restrict draft/internal opportunities for crew viewers.
- Supplier order actions do not enforce a server-side state-transition graph.
- `templates/account/settings.html` refers to a nonexistent `user.profile`/profile image shape and is display-only.
- `templates/tour/upcomming_tours/tourist_arrival_pickup.html` reverses unnamespaced `pickup_plan_edit`; welcome-package templates reverse admin names even though admin URLs are not mounted.
- English, Arabic, and Persian legacy legal text is hard-coded in `home/views_v2.py`, not versioned/approved content.
- The legacy `states:Paktika` route renders misspelled `Paktieka.html`; Paktia has no equivalent route. Duplicate `New_and_Trending` URL declarations exist.

## 8. Readiness conclusion

The relaunch should be an incremental hardening and consolidation effort, not a rewrite. Preserve the live URLs and data, establish reproducible migrations, create private document storage/download boundaries, formalize permissions, repair payment and operational defects, and then switch the public brand/content shell. The detailed route, model, legacy, gap, risk, command, and execution maps are in the companion documents.
