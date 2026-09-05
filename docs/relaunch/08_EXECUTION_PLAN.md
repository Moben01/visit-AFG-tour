# Larmoond Relaunch — Execution Plan

**Audit date:** 2026-08-29
This is a sequencing and reuse plan only. No runtime implementation, schema change, content replacement or deployment is authorized by this audit.

## Classification definitions

- `EXISTING_AND_READY`: present, tested at a reasonable unit/integration level, and suitable to retain unchanged in the relaunch architecture. It may still receive brand copy/styling later.
- `EXISTING_NEEDS_FIX`: present and fundamentally appropriate, but a confirmed defect/security/quality issue blocks reliance on it.
- `EXTEND_EXISTING`: a solid existing foundation should be expanded; do not build a parallel workflow/model.
- `BUILD_NEW`: no adequate implementation exists and a new, scoped component is required.
- `REMOVE`: copied, unsafe, duplicate, misleading, or dead behavior should leave the active public/operational experience after compatibility/data checks.
- `DEFER`: not required until a real operational need and approved scope exist.

## Foundation, schema, security, and identity

| Required feature | Existing foundation | Classification | Planned outcome / acceptance |
|---|---|---|---|
| Reproducible Django schema history | Live ledger plus untracked home migrations; syncdb behavior | `BUILD_NEW` | Approved baseline migration history matching clean and production-like databases; no table/app-label rename; restore/rollback rehearsal. |
| Reference-data lifecycle | `post_migrate` roles/categories/courses | `EXISTING_NEEDS_FIX` | Controlled, idempotent migration/command with reviewed codes and no silent legacy recreation. |
| Email-first sign-in/signup/logout/password reset | allauth and custom user | `EXISTING_AND_READY` | Retain email-first mandatory-verification flow; update brand/email templates later and keep tests. |
| Case-insensitive email identity | model normalization and DB constraint | `EXISTING_AND_READY` | Preserve constraint; retire schema-changing management-command behavior. |
| Role and permission model | role string, staff/superuser, Django permissions, decorators | `EXTEND_EXISTING` | Approved least-privilege matrix/groups/object permissions; compatibility with current roles; boundary tests. |
| Role-aware dashboard router | `tour:dashboard` | `EXISTING_NEEDS_FIX` | Define precedence and approved/unapproved behavior for multi-profile users. |
| Customer account settings | existing route/template | `EXISTING_NEEDS_FIX` | Bind to real user/profile fields, support validated edits, correct nested URL, remove broken attributes/asset paths. |
| Private document storage | default public media only | `BUILD_NEW` | Private backend/location, non-guessable keys, no public URL, retention/backup policy. |
| Authorized private downloads | none; direct `.url` links | `BUILD_NEW` | Object-scoped download endpoints/proxy response, deny-by-default, audit/redaction/cache headers and tests. |
| Public editorial media library | `ManagedMedia` and content images | `EXTEND_EXISTING` | Keep separate from private storage; validate image type/size/alt/rights metadata. |
| Secure upload policy | basic Django file fields/forms | `BUILD_NEW` | Shared size/type/MIME/malware workflow and explicit allowed file rules; never log identifiers. |
| Privacy-safe audit logging | no complete audit subsystem | `BUILD_NEW` | Actor/action/object/status security events without PII/document contents; finance/document state traceability. |
| Data retention/deletion policy | none encoded | `BUILD_NEW` | Approved rules for leads, trips, bookings, passports, crew/supplier documents and logs; legal review. |

## Tours, trip planning, quotation, booking, and payment

| Required feature | Existing foundation | Classification | Planned outcome / acceptance |
|---|---|---|---|
| Tour categories and catalogue | `TourCategory`, `Tour`, `TourImage`, list/detail views | `EXTEND_EXISTING` | Repair routing/publishing/SEO; populate only real approved tours; keep current URLs or redirects. |
| Tour inclusions/exclusions/FAQs | existing child models/templates | `EXISTING_AND_READY` | Retain; add content quality/ordering tests as editor changes occur. |
| Canonical itinerary days | `ItineraryItem` | `EXTEND_EXISTING` | Enforce ordering/cardinality after data audit; use as canonical tour itinerary. |
| Customer itinerary customization | `UserItineraryItem`, edit flow | `EXISTING_NEEDS_FIX` | Restrict eligible resources, version/reprice safely, prevent duplicates; later consider delta model. |
| Tour search | home search/HTMX results | `EXISTING_AND_READY` | Retain; add metadata/accessibility/browser tests and real content. |
| Tour favourites | `User_favorite_tour`, HTMX | `EXISTING_NEEDS_FIX` | POST-only mutation, unique user/tour, concurrency and authorization tests. |
| Public trip builder | `TripRequest`, stops/preferences/entry plan | `EXTEND_EXISTING` | Add consent, rate/abuse controls, relational ownership and validated JSON while preserving UUID/session flow. |
| Operations trip-request queue | operations list/detail/update | `EXISTING_AND_READY` | Retain behavior; apply future least-privilege and indexing policy. |
| Route quotation/proposal | `RouteProposal`, proposal days, send/accept/reject | `EXTEND_EXISTING` | Proper FKs/audit, immutable sent snapshot, validity/currency/amount rules and branded customer delivery. |
| Proposal-to-booking conversion | current operations action | `EXISTING_AND_READY` | Retain and expand tests around idempotency/ownership when schema is stabilized. |
| Booking creation and server-side quote | `Booking`, `tour_booking` | `EXTEND_EXISTING` | Normalize statuses/currency/decimals and transactional inventory/price confirmation. |
| Customer bookings/dashboard | customer dashboard/tour list/detail | `EXISTING_NEEDS_FIX` | One modern shell, real data only, role-aware navigation, no theme/mock widgets. |
| Operations booking management | list/detail/status/payment/export | `EXTEND_EXISTING` | Split permissions, validate transitions, improve indexes/audit; keep CSV export. |
| Stripe-hosted card entry | Checkout redirect; no card storage | `EXISTING_AND_READY` | Retain Stripe-hosted collection; never add card fields. End-to-end settlement is separately classified below. |
| Stripe payment reconciliation/webhook | success/cancel/webhook | `EXISTING_NEEDS_FIX` | Match mode/account/session/reference/amount/currency, atomic idempotent ledger and replay/mismatch tests. |
| Manual/offline payment recording | Moderator/superuser operation | `EXISTING_NEEDS_FIX` | Finance-specific permission, evidence/audit, currency/decimal and reversal policy. |
| Booking CSV export | existing operations export | `EXISTING_AND_READY` | Retain with least-privilege and spreadsheet-injection/privacy checks. |
| Quote/itinerary PDF | none | `DEFER` | Build only after approved operational requirement, snapshot schema and private delivery design. |

## Traveller coordination

| Required feature | Existing foundation | Classification | Planned outcome / acceptance |
|---|---|---|---|
| Post-confirmation traveller document collection | two pre-arrival models/views | `EXISTING_NEEDS_FIX` | Secure storage first; canonical model bridge; collect only after confirmed/paid rules; owner/document-role tests. |
| Visa/invitation/insurance workflow | `PreArrivalRequirement` | `EXTEND_EXISTING` | Conditional requirements and review states, without publishing legal/visa claims. |
| Flight/emergency/medical details | `PreArrival` | `EXTEND_EXISTING` | Map needed fields into canonical secured workflow; minimize sensitive collection. |
| Arrival pickup planning | Driver/Operator/Vehicle/PickupPlan | `EXISTING_NEEDS_FIX` | Repair missing method/reverses/permissions; tested transition graph and authorized proof files. |
| Welcome package | `GiftItem`, `WelcomePackage` | `EXISTING_NEEDS_FIX` | Replace admin-dependent actions with application routes; real inventory/delivery states only. |
| Traveller support/case management | crew cases only; no customer case model | `BUILD_NEW` | Add only a scoped booking-linked support case/message workflow if operations confirms need; reuse user/booking permissions. |
| Traveller document PDF/download bundle | none | `DEFER` | Do not create a bundle until retention/private-delivery/legal needs are approved. |

## Workforce, guides, and suppliers

| Required feature | Existing foundation | Classification | Planned outcome / acceptance |
|---|---|---|---|
| Workforce profiles for guides/translators/hosts/drivers/etc. | `CrewMember`, roles, qualifications | `EXTEND_EXISTING` | Make canonical; approval gates and secure evidence; role-specific capability fields only where necessary. |
| Legacy public guide/translator applications | `TourGuide`/`Translator` forms | `REMOVE` | Redirect to authenticated crew onboarding after compatibility/data plan; stop public ID/CV uploads. |
| Legacy guide/translator/security records | three older models | `EXISTING_NEEDS_FIX` | Read-only compatibility and additive bridge to crew; remove active duplication only after reconciliation. |
| Crew documents/qualifications verification | current portal/operations reviews | `EXISTING_NEEDS_FIX` | Private downloads, dedicated reviewer permission, expiry/decision audit and approval gate. |
| Crew availability | `CrewAvailability` | `EXTEND_EXISTING` | Validate ranges/overlaps and index operational lookup. |
| Opportunities/applications/offers | full current workflow | `EXISTING_NEEDS_FIX` | Hide drafts/internal budgets; expiry/status transitions, approval and object tests. |
| Crew tour assignments | `CrewEngagement` | `EXTEND_EXISTING` | Canonical assignment; bridge direct Tour FKs and broken `TourGuideAssignment`. |
| Crew check-in/out, payments and reviews | engagement/payment/review models/views | `EXTEND_EXISTING` | Private proofs/receipts, verified customer review eligibility, finance permissions and audit. |
| Crew training/cases/notifications | current models/portals | `EXTEND_EXISTING` | Replace legacy seed content; restrict cases; safe internal notification links. |
| Supplier onboarding/profile | `ServiceSupplier` | `EXISTING_NEEDS_FIX` | Approval/role policy, secure verification documents and organization ownership. |
| Supplier services/assets/contracts/rates | current supplier network | `EXTEND_EXISTING` | Bridge accommodation/transport/fleet inventory, contract privacy/lifecycle and normalized rate units/currency. |
| Tour resource requirements and RFQs | requirement/RFQ/quote workflow | `EXTEND_EXISTING` | Approval, deadline/status, invited-supplier/quote rules and query indexes. |
| Service orders | `ServiceOrder` | `EXISTING_NEEDS_FIX` | Enforced atomic transition graph, voucher privacy and fulfillment audit. |
| Supplier invoices/reviews | current models/views | `EXTEND_EXISTING` | Private invoice access, finance review/reconciliation; reviews only for fulfilled orders. |

## Content, destinations, navigation, brand, and discoverability

| Required feature | Existing foundation | Classification | Planned outcome / acceptance |
|---|---|---|---|
| Central brand/public-site configuration | Extended `Main_things`, restricted Django admin, context processor and readiness checks | `EXISTING_NEEDS_FIX` | The reusable system is implemented in Task 2. Apply migration `home.0007`, grant the dedicated permission, and populate verified legal/contact/domain data plus supplied approved assets before readiness becomes green. |
| Modular homepage content | `ContentSection`/`ContentItem`, home renderer/editor | `EXTEND_EXISTING` | Replace approved copy/brand through content operations; real capability claims only. |
| Curated homepage destinations | `PopularPlace` and ordering | `EXISTING_AND_READY` | Retain; convert route references to canonical destinations while preserving aliases. |
| Dynamic destination pages | `ProvincePage`/sections/dynamic route | `EXTEND_EXISTING` | Populate reviewed pages, SEO and publishing workflow; no new destination model. |
| 37 legacy province page implementations | static views/templates | `REMOVE` | After dynamic parity, preserve old public paths as redirects/aliases; remove copied templates only after traffic/link verification. |
| Things-to-do editorial content | four model families and content editor | `EXISTING_NEEDS_FIX` | Consolidate to one typed content workflow additively; no fifth model. |
| Static visa/safety/entry/weather/legal claims | copied planning templates/hard-coded legal dictionary | `REMOVE` | Remove from public launch unless authoritative, owned, dated and approved content replaces it. Weather live integration is separately deferred. |
| Weather data integration | static page only | `DEFER` | Add only with a reliable sourced provider, operational owner and freshness/error behavior. |
| Official contact details | database contact/fallback placeholders | `EXISTING_NEEDS_FIX` | Publish only verified address/email/phone; remove all placeholders and old contacts. |
| Public enquiry form | `EnquireUs` capture | `EXTEND_EXISTING` | Private lead workflow, consent/rate controls, operations assignment and approved notifications. |
| Public enquiry-as-review feed | enquiry partial with fake counts | `REMOVE` | Never render lead messages/names publicly; verified reviews must come from completed engagement/order/tour records. |
| Testimonials/completed-tour claims | no valid implementation/data | `DEFER` | Publish only verified real post-service reviews/tours when data exists and consent is recorded. |
| Public header/footer/navigation | new v2 shell plus legacy shells | `EXISTING_NEEDS_FIX` | Official names/messages/colors, role-aware named URLs, mobile/RTL/accessibility and no dead links. |
| Customer/agent mock dashboard widgets | legacy theme templates | `REMOVE` | Remove hotel/flight/cruise counters, mock earnings/news/invoices and dead add actions. |
| Operations/crew/supplier shells | current portals | `EXTEND_EXISTING` | Apply official brand, permission-aware menus, noindex and responsive/accessibility QA. |
| Canonical URL policy and redirects | mixed current routes | `BUILD_NEW` | Lowercase hyphenated canonicals, preserved named aliases/301s, language/canonical tests. |
| Page titles/descriptions | generic head and limited model SEO fields | `EXTEND_EXISTING` | Per-page approved localized metadata and safe fallbacks. |
| Canonical/Open Graph/Twitter metadata | none | `BUILD_NEW` | Localized canonical/social metadata using real content/assets. |
| JSON-LD | none | `BUILD_NEW` | Organization/WebSite/Breadcrumb/Tour schema only from verified database facts. |
| Sitemap | none | `BUILD_NEW` | Published canonical destinations/tours/pages only; localized behavior tested. |
| `robots.txt` and private noindex policy | none globally; operations noindex only | `BUILD_NEW` | Explicit public/private rules; no customer/auth/crew/supplier/operations indexing. |
| PWA manifest/icons | legacy manifest/assets | `EXISTING_NEEDS_FIX` | Official Larmoond names/colors/icons/start URL and cache/update QA. |
| Public brand replacement | legacy settings/DB/templates/assets/translations/email/payment | `EXISTING_NEEDS_FIX` | Coordinated replacement using approved official identity; automated source/DB/rendered/build/email scan. |
| Old hostname behavior | existing defaults, no redirect config in repo | `BUILD_NEW` | Approved permanent redirects/canonical/TLS behavior; old host retained only in permitted infrastructure/history. |
| English copy quality | mixed new and copied theme copy | `EXISTING_NEEDS_FIX` | Professional natural English, operational review and no placeholders/unsupported claims. |
| Dari/Arabic/Pashto localization | `fa`/`ar` catalogs and RTL templates | `EXTEND_EXISTING` | Confirm actual launch languages, professional translations, terminology and RTL QA; add Pashto only if approved. |
| Unused templates/vendor/theme assets | known unreachable/dead assets | `REMOVE` | Staged cleanup after reference/build/browser audit; preserve recovery through Git. |

## Email, services, testing, and deployment

| Required feature | Existing foundation | Classification | Planned outcome / acceptance |
|---|---|---|---|
| Allauth transactional email | SMTP settings and overrides | `EXISTING_NEEDS_FIX` | Verified official sender/reply-to/domain, approved brand copy/translations, delivery/failure tests. |
| Enquiry/proposal/booking/document operational email | no explicit service | `BUILD_NEW` | Event-specific private templates, idempotency, no sensitive attachments/URLs and failure handling. |
| Business service layer | logic mainly in views/models | `EXTEND_EXISTING` | Extract payment, transitions, proposal conversion and document authorization incrementally with transaction tests. |
| Background jobs/retries | none | `DEFER` | Adopt only when real email/PDF/webhook operational volume requires it. |
| Fast unit/integration tests | 63 Django tests on SQLite | `EXTEND_EXISTING` | Keep suite; add all business workflows/permissions and remove debug print. |
| PostgreSQL test/migration suite | none | `BUILD_NEW` | CI database, clean build and upgrade rehearsal; constraints/index/query tests. |
| Browser/accessibility/HTMX/JS tests | none | `BUILD_NEW` | Critical public/customer/operations/crew/supplier journeys, links, RTL and accessibility. |
| Coverage reporting | none | `BUILD_NEW` | Coverage tooling and boundary-focused thresholds/reporting; not line-count-only. |
| Pinned dependency manifest | empty requirements/no lock | `BUILD_NEW` | Reproducible reviewed dependencies and security update process. |
| CI quality gate | none | `BUILD_NEW` | checks, migration drift, SQLite/PostgreSQL tests, diff/static/link/security scans. |
| Versioned deployment/runbook | settings comments/manual archives only | `BUILD_NEW` | Actual platform config, secrets, health, static/private media, backup/restore, rollback; no production deploy in feature tasks. |
| Observability/error monitoring | none evident | `BUILD_NEW` | Privacy-safe logs/errors/metrics and actionable health alerts. |
| Native mobile application | none required by mission | `DEFER` | Responsive/PWA web first; revisit only with approved business case. |

## Ordered implementation program

### Phase 0 — Preserve and prove the baseline

1. Commit this audit separately from the pre-existing dirty worktree.
2. Identify every target environment and obtain backups/sanitized schema evidence.
3. Produce pinned dependencies and a PostgreSQL test environment.
4. Establish/rehearse source-controlled migration baseline; do not create feature migrations before it is approved.
5. Add characterization tests for current routes, permissions, payment and data mappings.

### Phase 1 — Close critical privacy and financial boundaries

1. Private storage and authorized downloads; remove all direct private `.url` rendering.
2. Remove public enquiry feed and stop legacy public identity-document applications.
3. Approve and implement least-privilege role/permission matrix.
4. Harden Stripe reconciliation/idempotency and normalize amount/currency behavior.
5. Fix confirmed runtime routes/status errors and add regression tests.

### Phase 2 — Consolidate existing operational workflows

1. Bridge pre-arrival models into one secured workflow.
2. Bridge legacy providers/assignments into crew profiles/engagements.
3. Link accommodation/transport/fleet inventory to supplier resources without duplication.
4. Enforce crew/supplier approval, visibility and transition rules.
5. Add required constraints/indexes only after production duplicate/query analysis.

### Phase 3 — Curate and relaunch the public experience

1. Approve real contacts, tours, prices, destination content, capability claims and legal/editorial sources.
2. Populate existing content/tour/destination models; remove mock/stale/copy-pasted public behavior.
3. Implement official Larmoond shell, role-aware navigation, English/translation/RTL review.
4. Add canonical redirects, metadata, JSON-LD, sitemap, robots/noindex and manifest.
5. Run exhaustive legacy-term scans across source, database, rendered pages, emails and built artifacts.

### Phase 4 — Release engineering and verification

1. Version actual deployment configuration/runbook; validate secrets, TLS, private media, static build, health and observability.
2. Run SQLite plus PostgreSQL suites, migration upgrade rehearsal, browser/accessibility/link/SEO/security tests.
3. Test backups/restores and rollback timing.
4. Conduct manual role/document/payment/content verification with non-customer test data.
5. Production deployment remains a separate explicitly approved task.

## Program rules

- Every implementation task must inspect and extend these current models/workflows before proposing new ones.
- Every schema change must be additive/reversible and follow the baseline migration approval.
- Every permission or business workflow change requires positive and negative tests.
- No real customer data may appear in fixtures, screenshots, logs or audit artifacts.
- No contact, price, review, statistic, licence, visa/security/legal/weather/entry claim may be invented.
- Old URLs remain working through compatibility or redirects; internal Django labels/tables are not renamed during public rebrand.
