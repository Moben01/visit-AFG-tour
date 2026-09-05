# Larmoond Relaunch — Existing Model Map

**Audit date:** 2026-08-29
The working tree defines 78 first-party Django models: 1 in `accounts`, 14 in `home`, 55 in `tour`, and 8 in `things_to_do`. `states` and `play_your_trip` contain no models.

## Accounts

| Model | Purpose, relationships, and constraints | Reuse decision |
|---|---|---|
| `accounts.CustomUser` | Extends `AbstractUser`; email is unique and normalized; `Lower(email)` uniqueness constraint; string role field `my_choice_field` (`Tourist`, `Guide`, `Translator`, `Operator`, `Moderator`). Also inherits groups, permissions, staff and superuser flags. | Reuse. Rename the role field only through an additive compatibility migration; define formal role/permission policy first. |

## Home, content, destinations, and trip planning

| Model | Purpose, relationships, and constraints | Reuse decision |
|---|---|---|
| `Main_things` | Existing legacy contact table, extended by `home.0007_site_and_brand_configuration` into the canonical brand/public-site configuration. A nullable unique `singleton_key` identifies one canonical row while preserving historical rows and the misspelled legacy columns. | Reuse as the single source for brand, verified legal/contact/domain/social data, approved assets and display controls. Do not create another organization/settings model. |
| `ContentSection` | Keyed, ordered, active content section with title/body/link/image and timestamps; key unique. | Reuse as the primary modular page-content container. |
| `ContentItem` | Ordered child content for a section with text, links, image and active state. | Reuse. |
| `ProvincePage` | Slug-unique dynamic destination page with summary/body/hero/SEO fields and published state. | Reuse as the destination-page source of truth. |
| `ProvincePageSection` | Ordered child sections for a province page. | Reuse. |
| `ManagedMedia` | General content library file, category, alt text and attribution-like metadata. | Reuse for public/editorial assets only; never mix with private traveller/workforce files. |
| `PopularPlace` | Ordered home destination card; can point to a named route, external URL, or `ProvincePage`; active state. | Reuse as a curated navigation layer. |
| `PlaceImage` | Gallery child of `PopularPlace`. | Reuse where a destination card genuinely needs a gallery; avoid duplicating `ProvincePageSection` media. |
| `TripRequest` | UUID public identifier; traveller/contact/budget/date/status fields; scalar `user_id`, `assigned_expert_id`, and `booking_id`; timestamps. | Reuse and extend. Add safe nullable relationships while preserving scalar values during migration. |
| `TripStop` | Ordered destination/nights/notes child of a request; unique `(trip_request, position)`. | Reuse. |
| `TripPreference` | One-to-one request preferences; JSON interests, accommodation, transport, guide and other choices. | Reuse; validate JSON shapes. |
| `EntryPlan` | One-to-one entry/visa/arrival plan linked to request; scalar confirmer ID. | Reuse only for operational planning; keep official/legal claims outside this record. |
| `RouteProposal` | Quotation/proposal linked to request with status, validity, public pricing and internal notes; scalar booking/creator IDs. | Reuse and extend with proper relationships, immutable sent snapshots, currency/amount precision, and audit history. |
| `RouteProposalDay` | Ordered proposed route days. | Reuse. |

## Tours, bookings, traveller coordination, and legacy providers

| Model | Purpose and important relationships | Reuse decision |
|---|---|---|
| `TourCategory` | Tour taxonomy with title, description, image and slug. | Reuse. |
| `Translator` | Legacy provider profile with PII, ID number, CV, image, languages, approval, experience and price. | Bridge to `CrewMember`/roles/qualifications/documents, then remove from active workflow only after migration. |
| `TourGuide` | Legacy guide profile with contact/ID/passport/CV/image, provinces/languages/approval/price. | Bridge to `CrewMember`; do not build another guide model. |
| `SecurityGuard` | Legacy guard profile, public image, private ID document, approval/availability/price. | Bridge to `CrewMember`. |
| `EntryTicket` | Tour-linked ticket/product pricing. | Reuse or generalize through `ServiceRequirement` only after mapping existing data. |
| `Permit` | Tour-linked permit and uploaded document. | Reuse operationally; store the document privately. |
| `Tour` | Central catalogue record: category, image, slug, schedule/dates, descriptions, multi-select provinces, duration fields, price, availability, map text, and direct guide/guard/translator/ticket/permit links. | Reuse as the product aggregate. Remove direct workforce assignments only after bridging to engagements/requirements. |
| `User_favorite_tour` | User/tour/favourite flag. | Reuse; add unique `(user, tour)` and a matching lookup index. |
| `TourImage` | Tour gallery. | Reuse. |
| `Booking` | Tour/user, copied traveller details/counts, booking state, quote/payment fields and notes. | Reuse and extend; normalize status choices, currency and decimal amounts; index customer/operations queries. |
| `Accommodation` | Legacy accommodation option related to tours, features, price and image. | Reuse as customer-facing itinerary inventory or bridge to approved supplier services/assets; do not duplicate. |
| `Transport` | Legacy transport option related to tours, features, price and image. | Same approach as accommodation. |
| `Meal` | Tour meal option and price. | Reuse. |
| `Logistic` | Tour logistics item and price. | Reuse, with a clear relationship to service requirements/orders. |
| `ItineraryItem` | Tour day with route/content, accommodation, transport, meals, logistics, image and date/duration fields. | Reuse as canonical itinerary day; add tour/day ordering constraints. |
| `UserItineraryItem` | Near-copy of an itinerary day customized for one user, repeating most fields. | Existing duplication. Preserve, but move toward a delta/override model after data analysis. |
| `Frequently_asked_questions` | Tour FAQ child. | Reuse; naming can remain internal until a planned migration. |
| `EnquireUs` | Tour enquiry containing full name, email, phone, message, response flag and creation time. | Reuse as private lead data; never render as a public review/testimonial. |
| `Includes`, `Excludes` | Simple tour child labels. | Reuse; possible future consolidation is low priority. |
| `Ready_tour_for_booking` | One-to-one-in-practice readiness/custom-tour staging; `unique_together` is user only. | Existing-needs-fix. Determine intended cardinality before migration. |
| `Languages` | Language and price. | Reuse or bridge to crew qualifications/rates; avoid parallel language taxonomies. |
| `TourGuideInterest` | User expression of interest in a tour. | Bridge into crew applications. |
| `TourGuideAssignment` | Tour/bonus/status assignment but no guide field. | Structurally incomplete; replace active use with `CrewEngagement` after compatibility review. |
| `AccommodationImage`, `TransportImage` | Galleries for legacy resources. | Reuse with their parent inventory. |
| `PreArrivalRequirement` | Booking-linked passport, visa, insurance, invitation, arrival and review workflow with conditional requirements. | Prefer as the canonical extendable pre-arrival record after security/data mapping. |
| `PreArrival` | Second booking-linked pre-arrival record with passport, visa, mandatory flight ticket and emergency/medical data. | Duplicated workflow. Bridge fields to one canonical model; no destructive merge until production data is assessed. |
| `Driver`, `Operator`, `Vehicle` | Pickup resource records, each with contact/vehicle details and public images. | Reuse for dispatch, or link to approved crew/supplier resources; avoid another fleet model. |
| `PickupPlan` | One-to-one booking pickup assignment/status/check-in proof/notes. | Reuse; repair missing status method and permission model. |
| `GiftItem` | Welcome gift inventory and price/photo. | Reuse. |
| `WelcomePackage` | Booking package with gifts, status, delivery data and photo. | Reuse. |

## Workforce and crew

| Model | Purpose and important relationships | Reuse decision |
|---|---|---|
| `EmployeeProfile` | Internal employee profile associated with a user. | Reuse for employees, distinct from independent crew. |
| `CrewRole` | Code/name/description taxonomy. | Reuse; seed through controlled migration/command rather than `post_migrate`. |
| `CrewMember` | User-linked workforce identity, profile, location/languages, verification, roles and operational fields. | Canonical workforce profile. Extend rather than rebuilding guide/translator/host roles. |
| `CrewQualification` | Crew role qualification, evidence, verification and expiry data. | Reuse; private evidence/downloads. |
| `CrewDocument` | Typed crew document with file, expiry and verification. | Reuse only with private storage and object-level authorization. |
| `CrewAvailability` | Crew date range/status/notes. | Reuse; add range validation and overlap/index strategy. |
| `CrewOpportunity` | Tour/role opportunity with location, dates, capacity, public/internal details, budget, status and explicit status/start index. | Reuse; hide non-open records from crew. |
| `CrewApplication` | Crew application to opportunity with status and uniqueness. | Reuse; add operations status/query indexes where justified. |
| `CrewOffer` | Application offer, rates, expiry and response. | Reuse; enforce expiry/status transitions. |
| `CrewEngagement` | Tour/crew/role assignment, dates, rate/status/check-in/out; indexed by crew/start/end and validates overlap. | Canonical assignment model. |
| `CrewPayment` | Engagement payment and receipt. | Reuse; private receipt storage and normalized currency/amount. |
| `CrewReview` | Engagement review/rating. | Reuse as a verified post-service review, unlike enquiries. |
| `TrainingCourse` | Training definition and required roles. | Reuse; legacy seeded row must be migrated. |
| `CrewTrainingRecord` | Crew completion/score/certificate. | Reuse; private certificate handling. |
| `CrewCase` | Crew support/incident case. | Reuse with restricted visibility and audit history. |
| `CrewNotification` | Crew notification with optional URL/read state. | Reuse; validate URLs are internal/authorized. |

## Suppliers and procurement

| Model | Purpose and important relationships | Reuse decision |
|---|---|---|
| `SupplierCategory` | Code/name taxonomy. | Reuse; controlled reference-data seeding. |
| `ServiceSupplier` | User-linked supplier organization/profile, status, contact/location/tax/bank-like operational details and categories. | Canonical supplier profile. |
| `SupplierDocument` | Supplier verification document/expiry/file. | Reuse privately. |
| `SupplierService` | Supplier service offering, unit/capacity/price/currency/availability. | Reuse. |
| `SupplierAsset` | Supplier asset/vehicle/room/equipment record. | Reuse; bridge legacy accommodation/transport inventory. |
| `SupplierContract` | Supplier contract terms, dates, currency, file and status. | Reuse privately; add lifecycle controls. |
| `SupplierRate` | Contract rate by service/date/unit. | Reuse. |
| `ServiceRequirement` | Tour operational requirement with category, quantities/dates/specification/budget/status. | Reuse as procurement demand. |
| `RequestForQuote` | Requirement RFQ, invited suppliers, deadline and status. | Reuse. |
| `SupplierQuote` | Supplier RFQ response with price, notes, validity and attachment. | Reuse; enforce one/versioning policy and private attachment access. |
| `ServiceOrder` | Selected quote/supplier order with status, amounts, dates and voucher. | Reuse; implement server-side transition graph. |
| `SupplierInvoice` | Service-order invoice, amount/status and attachment. | Reuse privately; add reconciliation controls. |
| `SupplierReview` | Service-order supplier rating/review. | Reuse as verified operational feedback. |

## Things-to-do content

Four models repeat the same basic content shape (title, image, description, location, multi-select province values), each with its own image child:

| Parent | Image child | Assessment |
|---|---|---|
| `Best_places_for_visit` | `Best_places_for_visit_images` | Duplicate content workflow. |
| `Top_things_to_do_in_province` | `Top_things_to_do_in_province_images` | Duplicate; additionally carries a price. |
| `Popular_Tourist` | `Popular_Tourist_images` | Duplicate. |
| `Best_Selling` | `Best_Selling_images` | Duplicate. |

Do not add a fifth content type. Extend `ContentSection`/`ContentItem` or introduce a single typed destination-content model through an additive migration and compatibility layer.

## Duplicate/overlapping model and workflow map

| Overlap | Recommended source of truth |
|---|---|
| `TourGuide`, `Translator`, `SecurityGuard`, interests/assignments vs crew roles/applications/engagements | `CrewMember` + `CrewRole` + `CrewApplication` + `CrewEngagement`; retain legacy adapters until data is migrated. |
| `PreArrivalRequirement` vs `PreArrival` | One secured booking pre-arrival aggregate, likely extending `PreArrivalRequirement`; bridge all fields first. |
| `Accommodation`/`Transport`/Driver/Vehicle vs supplier services/assets | Keep customer itinerary inventory but link it to verified `ServiceSupplier` offerings/assets; do not duplicate records. |
| `PopularPlace`/`ProvincePage` vs 37 static state views/templates | `ProvincePage` for content, `PopularPlace` for curation; preserve old routes as redirects/aliases only after pages exist. |
| Four things-to-do parent/image pairs | One typed content workflow backed by existing content infrastructure. |
| `ItineraryItem` vs full-copy `UserItineraryItem` | `ItineraryItem` canonical; future user override/delta model after data migration. |
| `Main_things` vs content/contact centre | Content/contact centre. |
| Django admin vs custom operations content centre | Custom operations centre for public content/business workflows; admin only for controlled support if mounted. |
| Direct Tour provider FKs vs crew engagements and service requirements | Engagements/requirements; preserve compatibility for existing tours. |

## Database-backed content and migration state

The local PostgreSQL database was inspected in a read-only transaction.

| Data family | Count/state |
|---|---|
| Users | 3 (2 Tourist, 1 Moderator). Legacy strings exist in account identities; values omitted. |
| `ContentSection` / `ContentItem` / `PopularPlace` | 10 / 9 / 8, all active. |
| Province pages/media/trip planning | 0 business rows. |
| Tours/bookings/itineraries/providers/pre-arrival | 0 business rows. |
| Workforce/supplier | 13 roles, 13 supplier categories, 2 training courses; all transactional records 0. |
| Things-to-do | 0 rows. |

The database migration ledger records `accounts` 0001–0002, `home` 0001–0006, `things_to_do` 0001–0003, and `tour` 0001–0011. In the working tree, only `home/migrations/0001`–`0006` plus `__init__.py` exist, and the whole directory is untracked. No source migration package exists for `accounts`, `tour`, or `things_to_do`. The database nevertheless has the current newer tour tables, consistent with the source comment that legacy deployments use `migrate --run-syncdb`.

`makemigrations --check --dry-run` reports “No changes detected” because apps without migration modules are treated as unmigrated; this is not proof of a reproducible schema. Before any schema change, establish an approved baseline/fake-in migration plan against copies of every target database.

## Existing and missing indexes/constraints

Existing explicit strengths include case-insensitive email uniqueness, trip-stop position uniqueness, selected crew/application/engagement constraints, and an explicit `CrewOpportunity(status, start_date)` plus `CrewEngagement(crew_member, start_date, end_date)` index.

High-value gaps to validate with query plans before adding migrations:

- unique/index `(user, tour)` on favourites;
- ordered uniqueness/index `(tour, day/order)` on itinerary days;
- uniqueness/index for user itinerary overrides;
- booking composites used by dashboards, such as `(user, situation)` and operations status/payment/date filters;
- enquiry `(tour, responded, date_created)`;
- crew availability range lookups, applications by status, offers by status/expiry, training/case/notification queues;
- supplier status/category, RFQ deadline/status, quote selection, service-order status/date, and invoice status queues;
- scalar trip-request ownership/assignment/booking lookup fields until converted to real foreign keys.

Potential constraints also need correction: `Ready_tour_for_booking` is unique by user only; `TourGuideAssignment` lacks a guide; favourites and user itinerary copies allow duplicates; status fields use inconsistent casing/free-form patterns; and JSON/multi-select province values are not relationally validated.
