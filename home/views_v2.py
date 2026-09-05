from datetime import date, timedelta
from pathlib import Path

from PIL import Image
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_language
from django.views.decorators.http import require_GET, require_POST

from tour.models import CrewReview, Tour, TourCategory, TourGuide, User_favorite_tour

from .homepage import public_featured_tours

from .models import (
    EntryPlan,
    Main_things,
    PopularPlace,
    RouteProposal,
    TripPreference,
    TripRequest,
    TripStop,
)
from .trip_forms import EntryPlanForm, TripPreferenceForm, TripRequestForm, TripStopFormSet


def _localized_template(standard, rtl):
    return rtl if get_language() in {"fa", "ar"} else standard


def _favorite_count(request):
    if not request.user.is_authenticated:
        return 0
    return User_favorite_tour.objects.filter(user=request.user, favorite=True).count()


def _manifest_icon(configuration):
    asset = configuration.logo_symbol
    if not asset:
        return None
    extension = Path(asset.name).suffix.lower()
    if extension == ".svg":
        return {
            "src": configuration.logo_symbol_url,
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any",
        }
    if extension not in {".png", ".webp"}:
        return None
    try:
        asset.open("rb")
        width, height = Image.open(asset).size
    except (OSError, ValueError):
        return None
    finally:
        try:
            asset.close()
        except (AttributeError, OSError):
            pass
    if width != height or width < 192:
        return None
    return {
        "src": configuration.logo_symbol_url,
        "sizes": f"{width}x{height}",
        "type": "image/png" if extension == ".png" else "image/webp",
        "purpose": "any",
    }


@require_GET
def site_manifest(request):
    configuration = Main_things.get_solo()
    payload = {
        "name": configuration.official_brand_name,
        "short_name": configuration.short_brand_name,
        "start_url": reverse("home:home"),
        "scope": reverse("home:home"),
        "display": "standalone",
        "theme_color": "#072720",
        "background_color": "#FFFFFF",
    }
    if configuration.hero_description:
        payload["description"] = configuration.hero_description
    icon = _manifest_icon(configuration)
    if icon:
        payload["icons"] = [icon]
    response = JsonResponse(payload, content_type="application/manifest+json")
    response["Cache-Control"] = "public, max-age=300"
    return response


def home_view(request):
    categories = TourCategory.objects.all()
    configuration = Main_things.get_solo()
    destinations = (
        PopularPlace.objects.filter(is_active=True)
        .exclude(description__isnull=True)
        .exclude(description="")
        .exclude(Q(preview_image="") & Q(static_image=""))
        .order_by("display_order", "title", "pk")[:8]
    )
    public_hosts = TourGuide.objects.none()
    if configuration.show_team_section:
        public_hosts = (
            TourGuide.objects.filter(is_approved=True, is_active=True)
            .exclude(profile_image="")
            .exclude(bio="")
            .only(
                "id",
                "name",
                "provinces",
                "languages",
                "bio",
                "profile_image",
                "specialties",
            )
            .order_by("name", "pk")[:4]
        )

    approved_reviews = CrewReview.objects.none()
    if configuration.show_reviews:
        approved_reviews = (
            CrewReview.objects.filter(
                is_public=True,
                reviewer_type="tourist",
                engagement__status="completed",
                engagement__tour__bookings__user_id=F("reviewer_id"),
                engagement__tour__bookings__situation__in=("completed", "Reviewed"),
            )
            .exclude(comment="")
            .select_related("engagement__tour")
            .order_by("-created_at")
            .distinct()[:6]
        )

    context = {
        "get_tour_categories": categories,
        "get_main_things": configuration,
        "find_user_favorite": _favorite_count(request),
        "destinations": destinations,
        "featured_tours": public_featured_tours(limit=6),
        "public_hosts": public_hosts,
        "approved_reviews": approved_reviews,
        "hosting_service_groups": configuration.enabled_hosting_service_groups,
    }
    return render(request, _localized_template("index.html", "RTL/index.html"), context)


def search_view(request):
    query = request.GET.get("q", "").strip()
    check_in = request.GET.get("check_in", "").strip()
    try:
        guests = max(1, min(20, int(request.GET.get("guests", "1"))))
    except (TypeError, ValueError):
        guests = 1

    all_destinations = PopularPlace.objects.filter(is_active=True)
    if query:
        destination_results = all_destinations.filter(
            Q(title__icontains=query)
            | Q(province__icontains=query)
            | Q(description__icontains=query)
        )
        tour_results = (
            Tour.objects.filter(available=True)
            .filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            )
            .select_related("category")
            .distinct()[:12]
        )
    else:
        destination_results = all_destinations
        tour_results = Tour.objects.filter(available=True).select_related("category")[:12]

    context = {
        "query": query,
        "check_in": check_in,
        "guests": guests,
        "destination_results": destination_results,
        "tour_results": tour_results,
    }
    return render(
        request,
        _localized_template("home/search_results.html", "RTL/search_results.html"),
        context,
    )


def _safe_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _trip_request_for_visitor(request, public_id):
    trip_request = get_object_or_404(
        TripRequest.objects.prefetch_related(
            "stops__destination",
            "proposals__days__destination",
        ),
        public_id=public_id,
    )
    if request.user.is_authenticated and (
        request.user.is_staff
        or request.user.is_superuser
        or request.user.my_choice_field in {"Operator", "Moderator"}
    ):
        return trip_request
    if request.user.is_authenticated and trip_request.user_id == request.user.pk:
        return trip_request
    session_ids = request.session.get("trip_request_ids", [])
    if str(trip_request.public_id) in session_ids:
        return trip_request
    raise PermissionDenied


def trip_builder_view(request):
    if request.method == "POST":
        trip_form = TripRequestForm(request.POST, prefix="trip")
        entry_form = EntryPlanForm(request.POST, prefix="entry")
        preference_form = TripPreferenceForm(request.POST, prefix="preferences")
        stop_formset = TripStopFormSet(request.POST, prefix="stops")
        if (
            trip_form.is_valid()
            and entry_form.is_valid()
            and preference_form.is_valid()
            and stop_formset.is_valid()
        ):
            with transaction.atomic():
                trip_request = trip_form.save(commit=False)
                if request.user.is_authenticated:
                    trip_request.user_id = request.user.pk
                trip_request.status = "submitted"
                trip_request.submitted_at = timezone.now()
                trip_request.save()

                entry_plan = entry_form.save(commit=False)
                entry_plan.trip_request = trip_request
                if entry_plan.selection_mode == "self":
                    entry_plan.status = "confirmed"
                    entry_plan.confirmed_at = timezone.now()
                entry_plan.save()

                preferences = preference_form.save(commit=False)
                preferences.trip_request = trip_request
                preferences.interests = preference_form.cleaned_data.get("interests", [])
                preferences.save()

                active_stop_forms = [
                    stop_form
                    for stop_form in stop_formset
                    if stop_form.cleaned_data and not stop_form.cleaned_data.get("DELETE")
                ]
                active_stop_forms.sort(
                    key=lambda item: item.cleaned_data.get("position") or 999
                )
                position = 1
                for stop_form in active_stop_forms:
                    TripStop.objects.create(
                        trip_request=trip_request,
                        destination=stop_form.cleaned_data["destination"],
                        position=position,
                        nights=stop_form.cleaned_data["nights"],
                        notes=stop_form.cleaned_data.get("notes", ""),
                    )
                    position += 1

            session_ids = request.session.get("trip_request_ids", [])
            session_ids.append(str(trip_request.public_id))
            request.session["trip_request_ids"] = session_ids[-12:]
            messages.success(
                request,
                "Your custom route request was saved and sent to our operations team.",
            )
            return redirect("home:trip_request_detail", public_id=trip_request.public_id)
    else:
        start_date = _safe_date(request.GET.get("check_in")) or (timezone.localdate() + timedelta(days=30))
        try:
            guests = max(1, min(20, int(request.GET.get("guests", "1"))))
        except (TypeError, ValueError):
            guests = 1
        user_initial = {
            "start_date": start_date,
            "end_date": start_date + timedelta(days=7),
            "adults": guests,
            "children": 0,
            "budget_tier": "flexible",
            "pace": "balanced",
        }
        if request.user.is_authenticated:
            user_initial.update(
                {
                    "full_name": request.user.get_full_name() or request.user.username,
                    "email": request.user.email,
                }
            )
        trip_form = TripRequestForm(prefix="trip", initial=user_initial)
        entry_form = EntryPlanForm(
            prefix="entry",
            initial={"selection_mode": "recommend", "transport_mode": "either"},
        )
        preference_form = TripPreferenceForm(
            prefix="preferences",
            initial={
                "accommodation_type": "advise",
                "transport_preference": "advise",
                "needs_local_guide": True,
            },
        )
        query = request.GET.get("q", "").strip()
        destination = PopularPlace.objects.filter(is_active=True, title__iexact=query).first()
        stop_formset = TripStopFormSet(
            prefix="stops",
            initial=[{"destination": destination, "nights": 2}] if destination else [{"nights": 2}],
        )

    return render(
        request,
        _localized_template("home/trip_builder.html", "RTL/trip_builder.html"),
        {
            "trip_form": trip_form,
            "entry_form": entry_form,
            "preference_form": preference_form,
            "stop_formset": stop_formset,
        },
    )


def trip_request_detail(request, public_id):
    trip_request = _trip_request_for_visitor(request, public_id)
    visible_proposals = trip_request.proposals.filter(status__in=("sent", "accepted")).prefetch_related(
        "days__destination"
    )
    return render(
        request,
        _localized_template("home/trip_request_detail.html", "RTL/trip_request_detail.html"),
        {
            "trip_request": trip_request,
            "visible_proposals": visible_proposals,
            "latest_proposal": visible_proposals.first(),
        },
    )


@login_required
def my_trip_requests(request):
    trip_requests = (
        TripRequest.objects.filter(user_id=request.user.pk)
        .prefetch_related("stops__destination", "proposals")
        .order_by("-submitted_at")
    )
    return render(
        request,
        _localized_template("home/my_trip_requests.html", "RTL/my_trip_requests.html"),
        {"trip_requests": trip_requests},
    )


@require_POST
def trip_request_action(request, public_id):
    trip_request = _trip_request_for_visitor(request, public_id)
    action = request.POST.get("action")
    if action == "accept":
        proposal = get_object_or_404(
            RouteProposal,
            trip_request=trip_request,
            status="sent",
            pk=request.POST.get("proposal_id"),
        )
        with transaction.atomic():
            trip_request.proposals.filter(status="sent").exclude(pk=proposal.pk).update(status="declined")
            proposal.status = "accepted"
            proposal.accepted_at = timezone.now()
            proposal.save(update_fields=("status", "accepted_at", "updated_at"))
            trip_request.status = "approved"
            trip_request.save(update_fields=("status", "updated_at"))
        messages.success(request, "The route proposal was accepted. Operations can now prepare the booking.")
    elif action == "changes":
        change_note = request.POST.get("change_note", "").strip()
        if not change_note:
            messages.error(request, "Describe the changes you need.")
        else:
            trip_request.notes = (
                (trip_request.notes + "\n\n") if trip_request.notes else ""
            ) + f"Traveller change request ({timezone.localtime():%Y-%m-%d %H:%M}): {change_note}"
            trip_request.status = "changes_requested"
            trip_request.save(update_fields=("notes", "status", "updated_at"))
            messages.success(request, "Your requested changes were sent to the operations team.")
    else:
        messages.error(request, "This route action is not valid.")
    return redirect("home:trip_request_detail", public_id=trip_request.public_id)


def set_currency(request):
    if request.method == "POST":
        currency = request.POST.get("currency", "").upper()
        if currency in {"USD", "EUR", "AFN"}:
            request.session["currency"] = currency

    target = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("home:home")
    if not url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        target = reverse("home:home")
    return redirect(target)


LEGAL_PAGES = {
    "privacy": {
        "en": {
            "title": "Privacy policy",
            "intro": "How Larmoond Travel and Tours handles information used to answer enquiries and deliver travel services.",
            "sections": (
                ("Information we collect", "We may collect account details, contact information, trip preferences, booking records, and documents you choose to provide for a requested travel service."),
                ("How we use information", "Information is used to answer requests, prepare itineraries, coordinate confirmed services, support travellers, prevent misuse, and meet applicable record-keeping duties."),
                ("Sharing and protection", "We share only the information reasonably needed by confirmed service providers or authorities involved in your trip. We use access controls and practical safeguards, but no online system can guarantee absolute security."),
                ("Your choices", "You may ask to review or correct your account information. You may also request deletion where the information is not required for an active booking, safety record, dispute, or legal obligation."),
            ),
        },
        "fa": {
            "title": "سیاست محرمیت",
            "intro": "چگونگی استفاده و نگهداری معلومات شما برای پاسخ‌گویی و ارائهٔ خدمات سفر.",
            "sections": (
                ("معلوماتی که جمع‌آوری می‌کنیم", "ممکن است معلومات حساب، راه‌های تماس، ترجیحات سفر، سوابق رزرو و اسنادی را که برای یک خدمت درخواستی می‌فرستید جمع‌آوری کنیم."),
                ("شیوهٔ استفاده", "این معلومات برای پاسخ به درخواست، تهیهٔ برنامه، هماهنگی خدمات تأییدشده، پشتیبانی مسافر، جلوگیری از سوءاستفاده و رعایت الزامات نگهداری سوابق استفاده می‌شود."),
                ("اشتراک و محافظت", "تنها معلومات ضروری با ارائه‌کنندگان تأییدشده یا مراجع دخیل در سفر شریک می‌شود. از کنترل دسترسی و تدابیر عملی استفاده می‌کنیم، اما هیچ سیستم آنلاین امنیت مطلق را تضمین نمی‌کند."),
                ("انتخاب‌های شما", "می‌توانید بررسی یا اصلاح معلومات حساب خود را درخواست کنید. در جایی که معلومات برای رزرو فعال، سابقهٔ ایمنی، اختلاف یا مکلفیت قانونی لازم نباشد، می‌توانید حذف آن را نیز بخواهید."),
            ),
        },
        "ar": {
            "title": "سياسة الخصوصية",
            "intro": "كيفية استخدام Larmoond Travel and Tours لمعلوماتك للرد على الطلبات وتقديم خدمات السفر.",
            "sections": (
                ("المعلومات التي نجمعها", "قد نجمع بيانات الحساب والاتصال وتفضيلات الرحلة وسجلات الحجز والمستندات التي تقدمها لخدمة سفر مطلوبة."),
                ("كيفية الاستخدام", "نستخدم المعلومات للرد على الطلبات وإعداد البرامج وتنسيق الخدمات المؤكدة ودعم المسافرين ومنع إساءة الاستخدام والوفاء بمتطلبات حفظ السجلات."),
                ("المشاركة والحماية", "لا نشارك إلا المعلومات اللازمة مع مقدمي الخدمات المؤكدين أو الجهات المشاركة في رحلتك. نستخدم ضوابط وصول وإجراءات عملية، لكن لا يمكن لأي نظام إلكتروني ضمان الأمان المطلق."),
                ("خياراتك", "يمكنك طلب مراجعة معلومات حسابك أو تصحيحها، كما يمكنك طلب حذفها عندما لا تكون مطلوبة لحجز نشط أو سجل سلامة أو نزاع أو التزام قانوني."),
            ),
        },
    },
    "terms": {
        "en": {
            "title": "Terms of use",
            "intro": "The conditions for using Larmoond Travel and Tours information, planning tools, and booking services.",
            "sections": (
                ("Travel information", "Destination content is provided for planning and may change. Travellers must check current visa, health, security, weather, and entry requirements with the relevant official authorities."),
                ("Bookings", "A request is not a confirmed booking until the itinerary, price, inclusions, payment terms, and availability are accepted and confirmed. Provider-specific conditions form part of that confirmation."),
                ("Traveller responsibilities", "Travellers are responsible for accurate information, valid documents, insurance decisions, respectful conduct, and following lawful safety instructions during a confirmed service."),
                ("Changes and availability", "Routes, schedules, accommodation, and local access can change. If a material change is required, available alternatives and any price effect will be communicated before acceptance whenever reasonably possible."),
            ),
        },
        "fa": {
            "title": "شرایط استفاده",
            "intro": "شرایط استفاده از معلومات، ابزارهای برنامه‌ریزی و خدمات رزرو Larmoond Travel and Tours.",
            "sections": (
                ("معلومات سفر", "محتوای مقصد برای برنامه‌ریزی است و ممکن است تغییر کند. مسافر باید شرایط فعلی ویزا، صحی، امنیتی، آب‌وهوا و ورود را با مراجع رسمی مربوط بررسی کند."),
                ("رزروها", "درخواست تا زمانی که برنامه، قیمت، خدمات شامل، شرایط پرداخت و موجودیت پذیرفته و تأیید نشده باشد رزرو قطعی نیست. شرایط ارائه‌کننده نیز بخشی از همان تأیید است."),
                ("مسئولیت مسافر", "مسافر مسئول معلومات درست، اسناد معتبر، تصمیم دربارهٔ بیمه، رفتار محترمانه و پیروی از رهنمودهای قانونی ایمنی در جریان خدمت تأییدشده است."),
                ("تغییرات و موجودیت", "مسیر، زمان‌بندی، اقامت و دسترسی محلی ممکن است تغییر کند. در صورت تغییر اساسی، گزینه‌های موجود و اثر احتمالی بر قیمت تا حد امکان پیش از پذیرش اطلاع داده می‌شود."),
            ),
        },
        "ar": {
            "title": "شروط الاستخدام",
            "intro": "شروط استخدام معلومات Larmoond Travel and Tours وأدوات التخطيط وخدمات الحجز.",
            "sections": (
                ("معلومات السفر", "محتوى الوجهات مخصص للتخطيط وقد يتغير. يجب على المسافر التحقق من متطلبات التأشيرة والصحة والأمن والطقس والدخول لدى الجهات الرسمية المختصة."),
                ("الحجوزات", "لا يصبح الطلب حجزاً مؤكداً حتى يتم قبول وتأكيد البرنامج والسعر والخدمات وشروط الدفع والتوفر. وتصبح شروط مقدم الخدمة جزءاً من ذلك التأكيد."),
                ("مسؤوليات المسافر", "يتحمل المسافر مسؤولية دقة معلوماته ووثائقه وقرار التأمين والسلوك المحترم واتباع تعليمات السلامة القانونية أثناء الخدمة المؤكدة."),
                ("التغييرات والتوفر", "قد تتغير المسارات والمواعيد والإقامة والوصول المحلي. عند الحاجة إلى تغيير جوهري، نوضح البدائل المتاحة وأثر السعر قبل القبول متى كان ذلك ممكناً."),
            ),
        },
    },
    "refund": {
        "en": {
            "title": "Cancellation and refunds",
            "intro": "How cancellation terms are presented and handled for confirmed travel services.",
            "sections": (
                ("Before payment", "The applicable cancellation schedule and any non-refundable supplier costs must be shown with the final itinerary before payment or confirmation."),
                ("Traveller cancellation", "Refund eligibility depends on the confirmed terms, notice date, and costs already committed to hotels, transport, permits, guides, or other providers."),
                ("Operator changes", "If a confirmed service cannot be delivered as agreed, available alternatives, credits, or refunds for the affected undelivered portion will be explained according to the confirmed terms."),
                ("Processing", "Approved refunds are returned through the available original payment channel where possible. Bank, card, and third-party processing times are outside the direct control of Larmoond Travel and Tours."),
            ),
        },
        "fa": {
            "title": "لغو و بازپرداخت",
            "intro": "شیوهٔ نمایش و تطبیق شرایط لغو برای خدمات سفر تأییدشده.",
            "sections": (
                ("پیش از پرداخت", "جدول لغو قابل تطبیق و هزینه‌های غیرقابل‌برگشت ارائه‌کنندگان باید همراه برنامهٔ نهایی و پیش از پرداخت یا تأیید نشان داده شود."),
                ("لغو از سوی مسافر", "امکان بازپرداخت به شرایط تأییدشده، تاریخ اطلاع و هزینه‌هایی وابسته است که قبلاً برای هتل، ترانسپورت، مجوز، راهنما یا ارائه‌کنندگان دیگر تعهد شده است."),
                ("تغییر از سوی برگزارکننده", "اگر خدمت تأییدشده مطابق توافق قابل ارائه نباشد، گزینهٔ جایگزین، اعتبار یا بازپرداخت بخش ارائه‌نشده مطابق شرایط تأییدشده توضیح داده می‌شود."),
                ("پردازش", "بازپرداخت تأییدشده در صورت امکان از همان مسیر پرداخت انجام می‌شود. زمان پردازش بانک، کارت و طرف سوم مستقیماً در کنترل Larmoond Travel and Tours نیست."),
            ),
        },
        "ar": {
            "title": "الإلغاء والاسترداد",
            "intro": "كيفية عرض شروط الإلغاء وتطبيقها على خدمات السفر المؤكدة.",
            "sections": (
                ("قبل الدفع", "يجب عرض جدول الإلغاء المطبق وأي تكاليف غير قابلة للاسترداد مع البرنامج النهائي قبل الدفع أو التأكيد."),
                ("إلغاء المسافر", "تعتمد أهلية الاسترداد على الشروط المؤكدة وتاريخ الإشعار والتكاليف الملتزم بها للفنادق والنقل والتصاريح والمرشدين ومقدمي الخدمات."),
                ("تغييرات المشغل", "إذا تعذر تقديم خدمة مؤكدة كما اتفق، يتم توضيح البدائل أو الرصيد أو استرداد الجزء غير المقدم وفق الشروط المؤكدة."),
                ("المعالجة", "تُعاد المبالغ المعتمدة عبر وسيلة الدفع الأصلية المتاحة متى أمكن. أوقات معالجة البنوك والبطاقات والجهات الخارجية ليست تحت السيطرة المباشرة لـ Larmoond Travel and Tours."),
            ),
        },
    },
}


def legal_page(request, page):
    page_data = LEGAL_PAGES.get(page, LEGAL_PAGES["terms"])
    language = get_language()
    localized = page_data.get(language, page_data["en"])
    context = {
        "page_title": localized["title"],
        "page_intro": localized["intro"],
        "sections": tuple(
            {"title": title, "paragraphs": (paragraph,)}
            for title, paragraph in localized["sections"]
        ),
    }
    return render(
        request,
        _localized_template("home/legal.html", "RTL/legal.html"),
        context,
    )


def custom_404_view(request, exception):
    return render(
        request,
        _localized_template("404.html", "RTL/404.html"),
        status=404,
    )


@login_required
def favorite_user_tour(request):
    if request.method == "POST":
        slug = request.POST.get("slug")
        if slug:
            tour = get_object_or_404(Tour, slug=slug)
            favorite, _ = User_favorite_tour.objects.get_or_create(
                user=request.user,
                tour=tour,
            )
            favorite.favorite = not favorite.favorite
            favorite.save(update_fields=["favorite"])

    favorites = (
        User_favorite_tour.objects.filter(user=request.user, favorite=True)
        .select_related("tour", "tour__category")
    )
    return render(
        request,
        "home/user-wish-list.html",
        {
            "find_user_favorites": favorites,
            "find_user_favorite": favorites.count(),
        },
    )


def rules_of_conduct(request):
    return render(request, "home/rules_of_conduct.html")
