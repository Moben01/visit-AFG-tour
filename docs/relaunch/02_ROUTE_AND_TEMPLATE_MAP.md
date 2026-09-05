# Larmoond Relaunch — Route and Template Map

**Audit date:** 2026-08-29
All routes below are current working-tree routes. Except `/i18n/setlang/`, DEBUG-only `/rosetta/`, and DEBUG-only `/media/`, application routes are inside `i18n_patterns`; English therefore begins with `/en/`.

## Root routing

| Prefix | Namespace/source | Notes |
|---|---|---|
| `/i18n/` | Django i18n | Language switching, outside the language prefix. |
| `/<lang>/accounts/` | allauth | Sign in/out, signup, email verification, password reset/change, reauthentication, passkeys and related optional account routes. Uses `templates/account/*`. |
| `/<lang>/` | `home` | Public shell, search, trip builder, legal and route-request pages. |
| `/<lang>/states/` | `states` | One dynamic province renderer plus legacy per-province views. |
| `/<lang>/play_your_trip/` | URL namespace `play_your_trip`; app declares `plan_your_trip` | Static planning pages; namespace declaration is inconsistent with include namespace. |
| `/<lang>/things_to_do/` | `things_to_do` | Static experience pages. |
| `/<lang>/accounts/` | project `accounts` | Adds a second `accounts/` inside the include, producing `/en/accounts/accounts/settings/`. |
| `/<lang>/tour/` | `tour` | Tours, bookings, payment, customer, crew, supplier and operations. |
| `/<lang>/favorite_user_tour` | unnamespaced root view | Legacy favourite page; no trailing slash. |
| `/<lang>/rules_of_conduct` | unnamespaced root view | Legacy page; no trailing slash. |

No `admin/`, sitemap, `robots.txt`, health/readiness, or API route is mounted.

## Home, search, legal and quotations

| Route/name | View/template | Access/notes |
|---|---|---|
| `/en/` — `home:home` | `home.views_v2.home_view` → `index.html` or `RTL/index.html`; includes `home/home2_v2.html`, `site/head_v2.html`, `site/header_v2.html`, `site/footer_v2.html`, `site/scripts_v3.html` | Public. Dynamic sections, places and available tours. |
| `/en/search/` — `home:search` | `search_view` → full home shell or `home/search_results_content.html` for HTMX | Public. |
| `/en/trip-builder/` — `home:trip_builder` | `trip_builder_view` → `home/trip_builder.html` or RTL counterpart | Public; associates signed-in user or session-held UUID. |
| `/en/my-route-requests/` — `home:my_trip_requests` | `home/my_trip_requests.html` | Login required. |
| `/en/route-requests/<uuid>/` — `home:trip_request_detail` | `home/trip_request_detail.html` | Owner, operations/staff, or session UUID. |
| `/en/route-requests/<uuid>/action/` — `home:trip_request_action` | POST redirect/HTMX response | Owner/session; proposal accept/reject. |
| `/en/currency/` — `home:set_currency` | Redirect | POST expected; stores USD/EUR/AFN in session. |
| `/en/privacy/`, `/en/terms/`, `/en/refunds/` | `legal_page` → `home/legal.html` or `RTL/legal.html` | Public; text hard-coded in Python. |
| `/en/favorite_user_tour` | `favorite_user_tour` → `home/user-wish-list.html` | Login required; legacy duplicate of newer favourite behavior. |
| `/en/rules_of_conduct` | `rules_of_conduct` → `home/rules_of_conduct.html` | Public. |

## Tours, booking, payment and customer coordination

| Route/name | View/template | Access/notes |
|---|---|---|
| `/en/tour/tours/<slug>/` — `tour:tour_category_list` | `tour-list.html` | Public category list; uses `.get()` and inconsistent filter semantics. |
| `/en/tour/tour-detail/<slug>/` — `tour:tour_details` | `tour-details.html`; HTMX enquiry response uses `tour/partials/endquires_list.html` | Public available tours; content preview exception. Publicly exposes enquiry names/messages. |
| `/en/tour/tour/<slug>/toggle-favorite/` | HTMX `tour/partials/favorite_button.html` | Login required; state-changing GET is accepted. |
| `/en/tour/tour/<slug>/tour_booking/` | `tour/tour-booking.html` | Login required; creates booking and server-calculated quote. |
| `/en/tour/translator_view/` | `tour_involve/translator.html` | Public legacy registration/upload. |
| `/en/tour/tour_guide_view/` | `tour_involve/tour_guide.html` | Public legacy registration/upload. |
| `/en/tour/dashboard/` | redirect router | Login required; crew profile wins, then supplier, operations role/staff, then customer. |
| `/en/tour/agent/dashboard/` | `tour_involve/tg_doc_dashboard.html` | Login required; legacy guide/operator dashboard. |
| `/en/tour/customer/dashboard/` | `tour/tourist_newsfeed.html` | Login required; customer overview. |
| `/en/tour/user_newsfeed/` | same customer area | Login required; overlapping route/workflow. |
| `/en/tour/payment/` and `/en/tour/payment/<booking_id>/` | `tour/payment.html` | Login required; first is a legacy no-ID route. |
| `/en/tour/payment/<booking_id>/checkout/` | redirect to Stripe Checkout | Booking owner. |
| `/en/tour/payment/<booking_id>/success/`, `/cancel/` | redirect/payment template behavior | Booking owner; success verifies Checkout session. |
| `/en/tour/payment/stripe/webhook/` | webhook response | CSRF exempt, Stripe signature checked. |
| `/en/tour/up_commoing_tours/`, `/en/tour/customer/tours/` | `tour/upcomming_tours/tourist_upcomming_tour.html` | Login required; duplicated list entry points and misspelled path/name retained. |
| `/en/tour/up_commoing_tours_more_info/<id>/` | `tourist_upcomming_tour_details.html` | Booking owner/staff. |
| `/en/tour/pre-arrival/<id>/` | `tourist_pre_arrival_info.html` | Paid booking owner/staff. |
| `/en/tour/pickup/<booking_id>/` | `tourist_arrival_pickup.html` | Owner/staff. |
| `/en/tour/pickup/<booking_id>/edit/`, `/status/` | same pickup template/redirect | Staff-only, inconsistent with Operator/Moderator portal access. |
| `/en/tour/welcome-package/<booking_id>/` | `tourist_wellcom_package.html` | Owner/staff; template contains admin reverses, but admin is not mounted. |
| `/en/tour/itenary_full_info/<id>/<booking_id>` | `tourist_itenary_info.html` | Owner/staff; no trailing slash and misspelled route. |
| `/en/tour/edit_itinerary/<itienary_id>/<user_id>` | `tour/customize-tour.html` | Login required; current user enforced unless staff. |
| `/en/tour/crew-review/<engagement_id>/` | `customer_crew_review` form | Engagement's booking owner. |

## Operations routes

Every route below is under `/en/tour/operations/`. The common shell is `templates/operations/base.html`; access is generally any staff/superuser/Operator/Moderator, with narrower checks only on selected actions.

### Dashboard and operational records

| Patterns | Templates |
|---|---|
| empty path | `operations/dashboard.html` |
| `route-requests/`, `<trip_id>/`, `<trip_id>/update/`, proposal `new/edit/send`, `<trip_id>/convert/` | `operations/trip_requests/list.html`, `detail.html`, shared forms |
| `bookings/`, `export/`, `<booking_id>/`, `details/`, `status/`, `payment/`, `pickup/`, `welcome-package/` | `operations/bookings/list.html`, `detail.html`, forms; export is CSV |
| `tours/`, `tours/<tour_id>/` | `operations/tours/list.html`, `detail.html` |
| `customers/`, `customers/<customer_id>/` | `operations/customers/list.html`, `detail.html` |
| `documents/` | `operations/documents/queue.html` |
| `pickups/` | `operations/pickups/queue.html` |
| `providers/` | `operations/providers/list.html` |
| `reports/` | `operations/reports.html` |

### Content centre

All use `operations/content/*` or `operations/resources/form.html`.

- `content/` dashboard and `content/contact/` site contact.
- `content/destinations/`: list, new, order, `<destination_id>/edit|delete|toggle`.
- `content/sections/`: list, new, `<section_id>/edit|delete|items`, item new; `content/items/<item_id>/edit|delete`.
- `content/provinces/`: list, new, `<page_id>/edit|delete|sections`, section new; `content/province-sections/<section_id>/edit|delete`.
- `content/media/`: list, new, `<media_id>/edit|delete`.
- `content/things/<kind>/`: list, new, `<record_id>/edit|delete` for the four parallel things-to-do model types.
- `content/tours/`: list, new, `<tour_id>/edit|delete`; itinerary new/order/edit/delete.
- `content/tour-categories/`: list, new, `<category_id>/edit|delete`.

Content access is superuser, Moderator, or `home.change_contentsection`, rather than the general operations rule.

### Workforce and training

- `resources/` → `operations/resources/dashboard.html`.
- `employees/`, `new/`, `<employee_id>/edit/` → list/shared form.
- `crew/`, `<crew_id>/`, document review, qualification verify → crew list/detail/forms.
- `opportunities/`, `new/`, `<opportunity_id>/`, `edit/`, plus tour-scoped create → opportunity list/detail/forms.
- application review and offer creation → shared forms.
- `engagements/`, `new/`, `<engagement_id>/`, `edit/`, `status/`, `payment/`, `review/`, plus tour-scoped create → engagement list/detail/forms.
- `training/`, course new/edit, training record new/edit and crew-scoped record create → training list/forms.
- `cases/`, `<case_id>/` → case list/detail.

### Suppliers and procurement

- `suppliers/`, new, detail, edit; nested service/asset/document/contract creation; document verification.
- `contracts/<contract_id>/rates/new/`.
- `tours/<tour_id>/resources/`, requirement new/edit.
- `requirements/<requirement_id>/rfq/`; `rfqs/`, `<rfq_id>/`.
- `quotes/<quote_id>/select/`.
- `service-orders/`, `<order_id>/`, status, review.
- `invoices/<invoice_id>/review/`.

These use `operations/suppliers/*`, `operations/procurement/*`, `operations/tours/resources.html`, and shared resource forms.

## Crew portal

All routes are under `/en/tour/crew/` and use `templates/crew/*` with the operations-style components.

- `onboarding/`; dashboard empty path; `profile/`.
- `profile/roles/add/`, `profile/documents/add/`, `profile/availability/add/`.
- `opportunities/`, `<opportunity_id>/`, `<opportunity_id>/apply/`.
- `applications/`.
- `offers/<offer_id>/`, `<offer_id>/respond/`.
- `assignments/`, `<engagement_id>/`, check-in, check-out.
- `training/`; `support/`; `support/new/`.

Onboarding requires login. Other routes require only that a crew profile exists; most do not require the profile to be approved. Opportunity detail does not filter out draft/internal opportunities.

## Supplier portal

All routes are under `/en/tour/supplier/` and use `templates/supplier/*`.

- `onboarding/`; dashboard empty path; `profile/`.
- `profile/services/add/`, `profile/assets/add/`, `profile/documents/add/`.
- `rfqs/`, `<rfq_id>/`.
- `orders/`, `<order_id>/`, `<order_id>/action/`, `<order_id>/invoices/add/`.

Onboarding requires login. Other routes require ownership of a supplier profile/child record; supplier order actions do not validate a strict transition graph.

## Destinations and static planning routes

### Dynamic destination

`/en/states/guide/<slug>/` → `states/province_detail.html`, backed by published `home.ProvincePage`. No rows currently exist.

### Legacy province routes

All are no-trailing-slash routes unless shown: `kabul`, `kabul_maping`, `bolg_seaction`, `balkh`, `team/`, `samangan`, `jawzjan`, `faryab`, `SarePol`, `Baghlan`, `Kunduz`, `Takhar`, `Badakhshan`, `parwan`, `maidan_wardak`, `bamyan`, `logar`, `kapisa`, `panjshir`, `daikundi`, `ghazni`, `paktika`, `khost`, `Nangarhar`, `Kunar`, `Laghman`, `Nuristan`, `Kandahar`, `Helmand`, `Zabul`, `Uruzgan`, `Nimroz`, `Paktika`, `Herat`, `Farah`, `Badghis`, and `Ghor`.

Each renders the same-cased `templates/states/<name>.html` except lowercase/uppercase `Paktika` map to `paktika.html` and misspelled `Paktieka.html`; localized Kabul/Kandahar/Helmand branches use selected RTL/Farsi templates. `kabul_maping` uses `kabul-map.html`, `bolg_seaction` uses `home/bolg_seaction.html`, and `team/` uses `states/team.html`.

Missing/inconsistent coverage: no Paktia route, two Paktika routes differing only by case, mixed-case URLs and route names, misspellings, no trailing-slash policy, and copied templates with raw links.

### Trip-planning pages

Under `/en/play_your_trip/`: `visa_guide`, `essentials`, `Accommodation`, `Getting_to_around_afg`, `safety`, `weather`, `currency`, `accessibility`, `afghanistan_attractions_passes`. Views render matching `play_your_trip/*.html` pages (case and underscores preserved). All are public static editorial/legal/safety content and need source verification before relaunch.

### Things-to-do pages

Under `/en/things_to_do/`: `Art_and_Culture/`, `Experiences/`, `food_and_drink/`, `New_and_Trending/`, `wellness-in-afg/`, `Shopping/`, `Sights_/`. The `New_and_Trending/` pattern/name is declared twice. Views render matching `things_to_do/*.html` templates and query one or more of the four parallel content model families.

## Template reachability and broken links

Template files with no explicit render/include/extend reference and no framework-convention role were identified as:

- `templates/partials/tour/_total_price_button.html`
- `templates/site/scripts_v2.html`
- `templates/states/Ghaznie.html`
- `templates/things_to_do/Itineraries.html`
- `templates/tour/tourist_dashboard.html`

Allauth override templates are convention-discovered and are not classified as unused merely because no literal reference exists.

Confirmed active reverse/link problems:

- `Tour.get_absolute_url()` reverses nonexistent `tour_detail` instead of `tour:tour_details`.
- Pickup template uses unnamespaced `pickup_plan_edit`.
- Welcome-package template reverses `admin:tour_welcomepackage_add/change` while no admin URL exists.
- Optional allauth override templates reference names not present in the installed resolver (`account_confirm_password_reset_code`, `account_verify_phone`, `account_change_phone`, `account_request_login_code`, and `account_signup_by_passkey`); these may remain dormant until those flows are enabled.
- Legacy state, things-to-do, guide dashboard, wishlist, and upcoming-tour templates contain many raw `*.html`, `assets/...`, `javascript:void(0)`, and `#` links that bypass Django routing or lead nowhere.

## Navigation consistency

- The new header/footer and operations shell use named URLs, but legacy inner pages often replace that navigation with theme-specific menus.
- Authenticated users of every role see customer-oriented “My bookings”; dashboard routing itself is role/profile based.
- “Become an expert” points to the public legacy guide form, not authenticated crew onboarding.
- Customer overview and trip-detail pages use different dashboard generations and terminology.
- Destination cards depend on stored route names, which currently preserve mixed-case legacy names.
- Route spellings alternate between `tour`, `tours`, `up_commoing`, `itenary`, `play_your_trip`, and the app-level `plan_your_trip` namespace.
