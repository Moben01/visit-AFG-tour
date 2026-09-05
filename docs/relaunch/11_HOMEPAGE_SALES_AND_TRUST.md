# Larmoond Relaunch — Homepage Sales and Trust Architecture

**Implementation date:** 2026-08-30
**Migration:** `home.0009_homepage_sales_configuration`

## Purpose and data ownership

The public homepage is the main sales and trust page for Larmoond Travel and
Tours. Its fixed English sales copy follows the approved launch brief. Brand,
legal, contact, language and display decisions still come only from the
canonical `home.Main_things` singleton described in
`09_BRAND_AND_SITE_CONFIGURATION.md`.

No duplicate tour, destination, guide, review or company-profile workflow was
created:

- tours and itineraries remain `tour.Tour` and `tour.ItineraryItem`;
- destinations remain `home.PopularPlace`;
- public hosts remain approved, active `tour.TourGuide` records;
- reviews remain `tour.CrewReview` records tied to completed crew engagements
  and completed customer bookings;
- contact, legal identity, licence display and operating switches remain
  `home.Main_things`.

## Homepage sequence

`templates/home/home2_v2.html` renders the approved sequence:

1. hero;
2. featured tours;
3. local-host positioning;
4. how it works;
5. hosting promise;
6. popular destinations;
7. approved local hosts, when available;
8. responsible and informed travel;
9. approved completed-journey reviews, or real operating evidence;
10. final planning call to action.

The page uses one `h1`; section titles use `h2`; card and step titles use `h3`.
Below-the-fold record images use lazy loading and decoding hints. All image URLs
come from the project's media or static storage; the page contains no external
image hotlinks and no autoplaying media, counters, simulated live status or
unsupported safety promises.

## Featured-tour publication contract

The tour application has no migration history and is synchronized as an
unmigrated application in this repository. Adding homepage-only fields directly
to `tour.Tour` would make a safe incremental migration ambiguous. The additive
`home.TourHomepageFeature` one-to-one companion therefore stores only homepage
presentation metadata:

- physical level;
- display order;
- active featured state.

It is edited inside the existing Operations tour editor, not through a second
tour-management screen. Unchecking the homepage option deactivates the feature
without deleting its metadata.

`home.homepage.public_featured_tours()` is the single publication service used
by both the page and launch-readiness command. A feature is public only when:

- the feature is active and has a supported physical level;
- the related tour is published (`available=True`);
- title, cover image, description, route and positive duration are present;
- the number of itinerary days exactly matches the declared day duration;
- a scheduled tour has valid, non-expired start and end dates; or the tour is a
  flexible-date tour.

The homepage renders no broken empty grid. When no feature satisfies the full
contract it shows the private-journey request path. This fallback does not make
the site launch-ready.

## Capability and trust gates

The singleton stores `enabled_hosting_services` as a validated list of approved
service codes. The admin presents this as checkboxes. No hosting service is
enabled by default, and the homepage renders only selected services. Actual
inclusions remain subject to the confirmed itinerary and quotation.

The licence claim appears only when the licence badge is enabled and both the
number and issuing authority are present. Guide cards require both approval and
public-active state plus a profile image and biography. Their query selects only
public fields; private telephone numbers, email addresses, identity numbers,
CVs, application files, rates and addresses are never passed to the template.

The review section requires all of the following:

- the public-review switch is enabled;
- the review is marked public;
- it was submitted by a tourist;
- its crew engagement is completed;
- the reviewer owns a completed or reviewed booking for the same tour;
- a non-empty comment exists.

The traveller's name and contact data are not displayed. When no review passes
these conditions, the page shows only available real evidence: completed
licence/legal identity, approved profiles, the connected operating workflow and
the itinerary-before-confirmation process.

## Destinations and images

The page preserves existing destination records and selects at most eight
active records with non-empty concise copy and a configured local image. Images
use responsive CSS aspect ratios and HTML `sizes`, and records may use the
existing WebP upload support. No format is fabricated when the source asset is
not available; content operators should prefer rights-cleared WebP originals
and retain source/provenance records outside public media.

## Launch readiness

Run the read-only gate with:

```text
python manage.py check_launch_readiness
```

It exits non-zero when required public settings are incomplete or fewer than
`minimum_featured_tours_for_launch` complete featured tours pass the same
publication service used by the homepage. The default threshold is three and
the supported administrative range is one to twelve. The command reports only
field labels and aggregate tour counts; it does not print configured values or
secrets and never modifies data.

Before changing the threshold, confirm that the selected tours represent real,
operable products. The empty-state CTA is a graceful public fallback, not a
waiver of the launch gate.

## Styling, accessibility and analytics

`static/css/larmoond-homepage.css` is scoped to `.lm-home`, mobile-first, and
uses the centralized brand tokens. Deep green carries trust and dark sections;
lime is limited to primary actions, verification cues and visible keyboard
focus. Layout breakpoints progressively enhance tour, process, destination,
host and evidence grids. Reduced-motion preferences disable ornamental
transitions.

Private-journey CTA tracking reuses the public shell's fixed action and
placement allowlists. Payloads contain only the event, action and placement; no
destination URL, query string, displayed text, contact value or personal data
is collected.

All new public strings are translated in the existing Dari and Arabic catalogs.
Deployments must run `compilemessages` using the established build process.

## Migration and verification

The migration is additive and reversible. It adds two fields to the existing
singleton and creates the homepage presentation table; it does not rewrite tour
or production content. Review `migrate --plan` against a production-like backup
because the audit records incomplete migration histories in other applications.

Recommended verification:

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --settings=visit_afg_core.test_settings
python manage.py check_launch_readiness
git diff --check
```

Before launch, an administrator must upload/verify rights-cleared images, enable
only services the operations team can deliver, approve public host profiles,
complete real legal/contact settings, and publish enough fully documented tours
to satisfy the readiness threshold.
