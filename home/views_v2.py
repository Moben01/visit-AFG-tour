from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_language

from tour.models import Tour, TourCategory, User_favorite_tour

from .models import Main_things
from .site_data import destination_items


def _localized_template(standard, rtl):
    return rtl if get_language() in {"fa", "ar"} else standard


def _favorite_count(request):
    if not request.user.is_authenticated:
        return 0
    return User_favorite_tour.objects.filter(user=request.user, favorite=True).count()


def home_view(request):
    categories = TourCategory.objects.all()
    context = {
        "get_tour_categories": categories,
        "get_main_things": Main_things.objects.last(),
        "find_user_favorite": _favorite_count(request),
        "destinations": destination_items(),
        "featured_tours": Tour.objects.filter(available=True).select_related("category").order_by("-created_at")[:6],
    }
    return render(request, _localized_template("index.html", "RTL/index.html"), context)


def search_view(request):
    query = request.GET.get("q", "").strip()
    check_in = request.GET.get("check_in", "").strip()
    try:
        guests = max(1, min(20, int(request.GET.get("guests", "1"))))
    except (TypeError, ValueError):
        guests = 1

    all_destinations = destination_items()
    if query:
        query_lower = query.casefold()
        destination_results = tuple(
            item
            for item in all_destinations
            if query_lower in item["name"].casefold()
            or query_lower in item["province"].casefold()
            or query_lower in item["summary"].casefold()
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
            "intro": "How AfghanAwaits handles information used to answer enquiries and deliver travel services.",
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
            "intro": "كيفية استخدام AfghanAwaits لمعلوماتك للرد على الطلبات وتقديم خدمات السفر.",
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
            "intro": "The conditions for using AfghanAwaits information, planning tools, and booking services.",
            "sections": (
                ("Travel information", "Destination content is provided for planning and may change. Travellers must check current visa, health, security, weather, and entry requirements with the relevant official authorities."),
                ("Bookings", "A request is not a confirmed booking until the itinerary, price, inclusions, payment terms, and availability are accepted and confirmed. Provider-specific conditions form part of that confirmation."),
                ("Traveller responsibilities", "Travellers are responsible for accurate information, valid documents, insurance decisions, respectful conduct, and following lawful safety instructions during a confirmed service."),
                ("Changes and availability", "Routes, schedules, accommodation, and local access can change. If a material change is required, available alternatives and any price effect will be communicated before acceptance whenever reasonably possible."),
            ),
        },
        "fa": {
            "title": "شرایط استفاده",
            "intro": "شرایط استفاده از معلومات، ابزارهای برنامه‌ریزی و خدمات رزرو AfghanAwaits.",
            "sections": (
                ("معلومات سفر", "محتوای مقصد برای برنامه‌ریزی است و ممکن است تغییر کند. مسافر باید شرایط فعلی ویزا، صحی، امنیتی، آب‌وهوا و ورود را با مراجع رسمی مربوط بررسی کند."),
                ("رزروها", "درخواست تا زمانی که برنامه، قیمت، خدمات شامل، شرایط پرداخت و موجودیت پذیرفته و تأیید نشده باشد رزرو قطعی نیست. شرایط ارائه‌کننده نیز بخشی از همان تأیید است."),
                ("مسئولیت مسافر", "مسافر مسئول معلومات درست، اسناد معتبر، تصمیم دربارهٔ بیمه، رفتار محترمانه و پیروی از رهنمودهای قانونی ایمنی در جریان خدمت تأییدشده است."),
                ("تغییرات و موجودیت", "مسیر، زمان‌بندی، اقامت و دسترسی محلی ممکن است تغییر کند. در صورت تغییر اساسی، گزینه‌های موجود و اثر احتمالی بر قیمت تا حد امکان پیش از پذیرش اطلاع داده می‌شود."),
            ),
        },
        "ar": {
            "title": "شروط الاستخدام",
            "intro": "شروط استخدام معلومات AfghanAwaits وأدوات التخطيط وخدمات الحجز.",
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
                ("Processing", "Approved refunds are returned through the available original payment channel where possible. Bank, card, and third-party processing times are outside the direct control of AfghanAwaits."),
            ),
        },
        "fa": {
            "title": "لغو و بازپرداخت",
            "intro": "شیوهٔ نمایش و تطبیق شرایط لغو برای خدمات سفر تأییدشده.",
            "sections": (
                ("پیش از پرداخت", "جدول لغو قابل تطبیق و هزینه‌های غیرقابل‌برگشت ارائه‌کنندگان باید همراه برنامهٔ نهایی و پیش از پرداخت یا تأیید نشان داده شود."),
                ("لغو از سوی مسافر", "امکان بازپرداخت به شرایط تأییدشده، تاریخ اطلاع و هزینه‌هایی وابسته است که قبلاً برای هتل، ترانسپورت، مجوز، راهنما یا ارائه‌کنندگان دیگر تعهد شده است."),
                ("تغییر از سوی برگزارکننده", "اگر خدمت تأییدشده مطابق توافق قابل ارائه نباشد، گزینهٔ جایگزین، اعتبار یا بازپرداخت بخش ارائه‌نشده مطابق شرایط تأییدشده توضیح داده می‌شود."),
                ("پردازش", "بازپرداخت تأییدشده در صورت امکان از همان مسیر پرداخت انجام می‌شود. زمان پردازش بانک، کارت و طرف سوم مستقیماً در کنترل AfghanAwaits نیست."),
            ),
        },
        "ar": {
            "title": "الإلغاء والاسترداد",
            "intro": "كيفية عرض شروط الإلغاء وتطبيقها على خدمات السفر المؤكدة.",
            "sections": (
                ("قبل الدفع", "يجب عرض جدول الإلغاء المطبق وأي تكاليف غير قابلة للاسترداد مع البرنامج النهائي قبل الدفع أو التأكيد."),
                ("إلغاء المسافر", "تعتمد أهلية الاسترداد على الشروط المؤكدة وتاريخ الإشعار والتكاليف الملتزم بها للفنادق والنقل والتصاريح والمرشدين ومقدمي الخدمات."),
                ("تغييرات المشغل", "إذا تعذر تقديم خدمة مؤكدة كما اتفق، يتم توضيح البدائل أو الرصيد أو استرداد الجزء غير المقدم وفق الشروط المؤكدة."),
                ("المعالجة", "تُعاد المبالغ المعتمدة عبر وسيلة الدفع الأصلية المتاحة متى أمكن. أوقات معالجة البنوك والبطاقات والجهات الخارجية ليست تحت السيطرة المباشرة لـ AfghanAwaits."),
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
