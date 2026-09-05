# Larmoond Relaunch — Brand and Public-Site Configuration

**Implementation date:** 2026-08-29
**Migration:** `home.0007_site_and_brand_configuration`

## Architecture decision

Task 2 extends the existing `home.Main_things` table instead of creating a second settings, company-profile, or organization model. The original `noumber` and `email` columns remain for database compatibility but are no longer the public template source.

The canonical record is identified by a nullable, unique `singleton_key` with the value `1`. This provides database enforcement for the active record without deleting or rewriting historical duplicate rows. `Main_things.get_solo()` returns the canonical row, bridges to the latest legacy row before migration, and returns unsaved safe defaults only when the table has no record.

Model and admin deletion of the canonical configuration are disabled. Saving a new configuration through the model reuses the existing canonical row.

## Managed fields

The single record provides these groups:

- Brand: official, short and Dari names; primary tagline; hero heading and description.
- Legal identity: legal and operating names; licence number, authority and document; office address, city and country.
- Contact: primary, booking and support email; primary, secondary, WhatsApp and emergency operations telephone; business hours.
- Domains: primary domain, legacy domain and canonical scheme.
- Social: Facebook, Instagram, LinkedIn, YouTube and Tripadvisor URLs.
- Approved assets: primary, reversed and monochrome logos; symbol; favicon; default social image.
- Operational display: licence, team, reviews and fixed-departure switches; public languages; default currency; enquiry response text; safety notice; an allowlisted set of deliverable homepage hosting services; and the minimum number of complete featured tours required for launch.

Homepage sales presentation extends this singleton through the additive
`home.0009_homepage_sales_configuration` migration. See
`11_HOMEPAGE_SALES_AND_TRUST.md` for the publication, privacy and readiness
contract.

Uploaded assets are organized below `MEDIA_ROOT`:

| Asset | Storage path | Accepted extensions |
|---|---|---|
| Logo variants | `brand/logos/` | SVG, WEBP, PNG |
| Symbol and favicon | `brand/icons/` | Symbol: SVG, WEBP, PNG; favicon: ICO, SVG, PNG |
| Social image | `brand/social/` | JPG, JPEG, PNG, WEBP |
| Public licence document | `brand/licence/` | PDF, JPG, JPEG, PNG |

Each file is limited to 10 MB. Only an intentionally public licence document may be uploaded here; this location must never be used for guide or traveller documents.

## Validation and readiness

The model validates all values before normal saves:

- email syntax and rejection of known example domains;
- telephone syntax, 7–15 digits, and known placeholder formats;
- host-only domains without scheme, path, port or email syntax;
- non-placeholder licence numbers and paired number/authority values;
- a primary domain different from the legacy domain;
- a non-empty, unique language list limited to `settings.LANGUAGES` and containing the Django default language;
- allowed asset extensions and maximum file size.

The admin displays a readiness warning while required brand, hero, legal identity, office, primary contact, primary domain and core asset fields are missing. Licence fields become required for readiness when the licence badge is enabled. Empty optional fields are omitted by the public templates; no contact, licence, logo, social or notice placeholder is substituted.

## Administration and permission

The project now mounts a dedicated Django `AdminSite` within the language-prefixed URL tree at `/admin/`. It registers only `Main_things`, so the task does not expose unrelated registrations from Django's default admin. The configuration is available at the named route `site_configuration_admin:home_main_things_changelist`, which redirects directly to the one add/change form.

## Public header and footer consumers

The global public shell reads brand assets, identity, contact details, licence display state, social profiles and active languages from `site_config`; it does not define a second configuration source. The header uses the uploaded primary horizontal logo on its light background and the uploaded symbol (falling back to the primary logo or configured short-name wordmark) at the smallest breakpoint. Missing contact, licence, asset and social values omit their complete UI row, including its label.

The public shell assets are isolated in `static/css/larmoond-public-shell.css` and `static/js/larmoond-public-shell.js`. Click tracking is limited to allowlisted WhatsApp and private-journey actions and fixed placement names. It never includes the destination URL, displayed text, user details, configured telephone/email values, or page query data. The JavaScript also maintains the mobile menu label/icon state and supports closing an open menu with Escape.

English, Dari and Arabic shell labels live in the existing `home` translation catalogs. Only languages selected in `active_public_languages` are rendered by the header; deployments must run the existing `compilemessages` build step after catalog changes.

Access requires all of the following:

- an active user;
- Django staff status;
- the `home.manage_site_configuration` permission.

Superusers satisfy the permission check. There is no admin delete action, historical rows are excluded from the queryset, and a second add form is refused once the canonical record exists. The former Operations “Site contact” URL is retained for route compatibility but redirects an authorized configuration manager to this restricted Django admin form.

## Template and metadata interface

`home.context_processors.site_navigation` exposes:

- `site_config` and the compatibility alias `get_main_things`;
- `site_public_languages` and `site_current_language_label`;
- `site_currency`;
- `site_canonical_url`;
- `site_default_social_image_url`;
- `site_social_links`.

The active site head, header, footer and home hero use these values conditionally. The head provides conditional canonical, Open Graph, favicon and Apple-icon references plus the dynamic `home:site_manifest`. The manifest derives its names and description from the singleton, uses the approved color tokens, omits an icon when none is configured, accepts SVG symbols as size `any`, and includes only square raster symbols of at least 192 pixels.

The centralized design tokens are in `static/css/brand-tokens.css`:

```css
:root {
  --brand-deep-green: #072720;
  --brand-lime: #9EDD05;
  --brand-white: #FFFFFF;
}
```

The existing `--aa-*` color variables map to these tokens for compatibility; filenames and broader legacy branding are intentionally left for the next task.

## Migration behavior and rollback

The forward data bridge selects the latest existing `Main_things` row as canonical. It copies legacy email and telephone values only when they pass conservative checks and are not the audited legacy email or known placeholder telephone. It does not create or delete records.

On rollback, the reverse operation fills blank legacy contact columns from the canonical fields and clears `singleton_key` before Django removes the added columns. This makes the migration schema- and data-reversible while preserving legacy compatibility.

Apply and verify with:

```text
python manage.py migrate home
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --settings=visit_afg_core.test_settings
```

Back up and rehearse against a production-like database before applying any migration. The Task 1 audit identified incomplete migration histories in some applications, so `migrate --plan` must be reviewed in the target environment first.

## Approved-asset readiness blocker

No supplied Larmoond SVG, WEBP, PNG or ICO asset files were present in the repository or task workspace during implementation. The only discovered bundle was the explicitly legacy `static/brand/afghanawaits/` set. It was not copied, relabelled or redrawn.

Before launch, an authorized administrator must upload the exact approved files to the configuration record (or a later approved task may add the supplied originals under `static/brand/larmoond/`). Validate logo contrast, favicon rendering, Apple icon dimensions, square PWA sizes (at least 192 and preferably 512 pixels), social-image crop, file provenance and browser cache behavior. Public readiness intentionally remains incomplete until these real assets and verified company data are supplied.
