from functools import wraps

from django.contrib import messages
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from home.models import (
    ContentItem,
    ContentSection,
    Main_things,
    ManagedMedia,
    PopularPlace,
    ProvincePage,
    ProvincePageSection,
)
from home.permissions import has_content_management_access
from things_to_do.models import (
    Best_Selling,
    Best_places_for_visit,
    Popular_Tourist,
    Top_things_to_do_in_province,
)

from .content_forms import (
    BestPlaceContentForm,
    BestSellingContentForm,
    ContentItemForm,
    ContentSectionForm,
    ManagedMediaForm,
    PopularPlaceContentForm,
    ProvincePageForm,
    ProvincePageSectionForm,
    TopThingContentForm,
    TourCategoryContentForm,
    ItineraryItemContentForm,
    TouristAttractionContentForm,
    TourWebsiteContentForm,
)
from .models import ItineraryItem, Tour, TourCategory


THING_TYPES = {
    "best-places": {
        "model": Best_places_for_visit,
        "form": BestPlaceContentForm,
        "title": "Best places to visit",
    },
    "top-things": {
        "model": Top_things_to_do_in_province,
        "form": TopThingContentForm,
        "title": "Top things to do",
    },
    "attractions": {
        "model": Popular_Tourist,
        "form": TouristAttractionContentForm,
        "title": "Tourist attractions",
    },
    "best-selling": {
        "model": Best_Selling,
        "form": BestSellingContentForm,
        "title": "Best-selling experiences",
    },
}


def content_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not has_content_management_access(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped


def _log_action(request, obj, action_flag, message):
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(obj.__class__).pk,
        object_id=obj.pk,
        object_repr=str(obj)[:200],
        action_flag=action_flag,
        change_message=message,
    )


def _form_response(
    request,
    *,
    form_class,
    title,
    back_url,
    instance=None,
    success_message="Content saved.",
    initial=None,
):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save()
            _log_action(
                request,
                obj,
                CHANGE if instance and instance.pk else ADDITION,
                success_message,
            )
            messages.success(request, success_message)
            return redirect(back_url)
    else:
        form = form_class(instance=instance, initial=initial)
    return render(
        request,
        "operations/content/form.html",
        {"form": form, "title": title, "back_url": back_url},
    )


def _delete_response(request, *, obj, title, back_url):
    if request.method == "POST":
        object_label = str(obj)
        _log_action(request, obj, DELETION, f"Deleted {object_label}.")
        obj.delete()
        messages.success(request, f"{object_label} was deleted.")
        return redirect(back_url)
    return render(
        request,
        "operations/content/confirm_delete.html",
        {"object": obj, "title": title, "back_url": back_url},
    )


@content_required
def content_dashboard(request):
    context = {
        "destination_count": PopularPlace.objects.count(),
        "active_destination_count": PopularPlace.objects.filter(is_active=True).count(),
        "section_count": ContentSection.objects.count(),
        "province_count": ProvincePage.objects.count(),
        "published_province_count": ProvincePage.objects.filter(is_published=True).count(),
        "media_count": ManagedMedia.objects.count(),
        "tour_count": Tour.objects.count(),
        "things_count": sum(config["model"].objects.count() for config in THING_TYPES.values()),
        "recent_media": ManagedMedia.objects.all()[:6],
        "recent_destinations": PopularPlace.objects.order_by("-updated_at")[:6],
        "can_manage_site_configuration": (
            request.user.is_staff
            and request.user.has_perm("home.manage_site_configuration")
        ),
    }
    return render(request, "operations/content/dashboard.html", context)


@content_required
def site_contact(request):
    if not (
        request.user.is_staff
        and request.user.has_perm("home.manage_site_configuration")
    ):
        raise PermissionDenied
    configuration = Main_things.objects.filter(singleton_key=1).first()
    if configuration:
        return redirect(
            reverse(
                "site_configuration_admin:home_main_things_change",
                args=(configuration.pk,),
            )
        )
    return redirect(
        reverse("site_configuration_admin:home_main_things_add")
    )


@content_required
def destination_list(request):
    queryset = PopularPlace.objects.select_related("province_page")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(province__icontains=query)
            | Q(description__icontains=query)
        )
    if status == "active":
        queryset = queryset.filter(is_active=True)
    elif status == "inactive":
        queryset = queryset.filter(is_active=False)
    page_obj = Paginator(queryset, 25).get_page(request.GET.get("page"))
    return render(
        request,
        "operations/content/destination_list.html",
        {"page_obj": page_obj, "destinations": page_obj.object_list, "query": query, "status": status},
    )


@content_required
def destination_form(request, destination_id=None):
    instance = get_object_or_404(PopularPlace, pk=destination_id) if destination_id else None
    return _form_response(
        request,
        form_class=PopularPlaceContentForm,
        instance=instance,
        title="Edit popular destination" if instance else "Add popular destination",
        back_url=reverse("tour:operations:content_destination_list"),
        success_message="Popular destination saved.",
    )


@content_required
def destination_delete(request, destination_id):
    return _delete_response(
        request,
        obj=get_object_or_404(PopularPlace, pk=destination_id),
        title="Delete popular destination",
        back_url=reverse("tour:operations:content_destination_list"),
    )


@require_POST
@content_required
def destination_toggle(request, destination_id):
    destination = get_object_or_404(PopularPlace, pk=destination_id)
    destination.is_active = not destination.is_active
    destination.save(update_fields=("is_active", "updated_at"))
    _log_action(request, destination, CHANGE, "Changed publication status.")
    messages.success(request, f"{destination} publication status updated.")
    return redirect("tour:operations:content_destination_list")


@require_POST
@content_required
def destination_order(request):
    changed = 0
    for destination in PopularPlace.objects.all():
        value = request.POST.get(f"order_{destination.pk}", "").strip()
        if value.isdigit() and destination.display_order != int(value):
            destination.display_order = int(value)
            destination.save(update_fields=("display_order", "updated_at"))
            _log_action(request, destination, CHANGE, "Changed display order.")
            changed += 1
    messages.success(request, f"Updated the order of {changed} destination(s).")
    return redirect("tour:operations:content_destination_list")


@content_required
def section_list(request):
    sections = ContentSection.objects.annotate(item_count=Count("items"))
    return render(request, "operations/content/section_list.html", {"sections": sections})


@content_required
def section_form(request, section_id=None):
    instance = get_object_or_404(ContentSection, pk=section_id) if section_id else None
    return _form_response(
        request,
        form_class=ContentSectionForm,
        instance=instance,
        title="Edit site section" if instance else "Add site section",
        back_url=reverse("tour:operations:content_section_list"),
        success_message="Site section saved.",
    )


@content_required
def section_delete(request, section_id):
    return _delete_response(
        request,
        obj=get_object_or_404(ContentSection, pk=section_id),
        title="Delete site section and its items",
        back_url=reverse("tour:operations:content_section_list"),
    )


@content_required
def section_items(request, section_id):
    section = get_object_or_404(ContentSection, pk=section_id)
    return render(
        request,
        "operations/content/item_list.html",
        {"section": section, "items": section.items.all()},
    )


@content_required
def item_form(request, item_id=None, section_id=None):
    instance = get_object_or_404(ContentItem, pk=item_id) if item_id else None
    initial = {"section": section_id} if section_id else None
    section_pk = instance.section_id if instance else section_id
    back_url = reverse("tour:operations:content_section_items", args=(section_pk,))
    return _form_response(
        request,
        form_class=ContentItemForm,
        instance=instance,
        initial=initial,
        title="Edit section item" if instance else "Add section item",
        back_url=back_url,
        success_message="Section item saved.",
    )


@content_required
def item_delete(request, item_id):
    item = get_object_or_404(ContentItem, pk=item_id)
    return _delete_response(
        request,
        obj=item,
        title="Delete section item",
        back_url=reverse("tour:operations:content_section_items", args=(item.section_id,)),
    )


@content_required
def province_list(request):
    pages = ProvincePage.objects.annotate(section_count=Count("sections"))
    return render(request, "operations/content/province_list.html", {"pages": pages})


@content_required
def province_form(request, page_id=None):
    instance = get_object_or_404(ProvincePage, pk=page_id) if page_id else None
    return _form_response(
        request,
        form_class=ProvincePageForm,
        instance=instance,
        title="Edit province page" if instance else "Add province page",
        back_url=reverse("tour:operations:content_province_list"),
        success_message="Province page saved.",
    )


@content_required
def province_delete(request, page_id):
    return _delete_response(
        request,
        obj=get_object_or_404(ProvincePage, pk=page_id),
        title="Delete province page",
        back_url=reverse("tour:operations:content_province_list"),
    )


@content_required
def province_sections(request, page_id):
    page = get_object_or_404(ProvincePage, pk=page_id)
    return render(
        request,
        "operations/content/province_section_list.html",
        {"page": page, "sections": page.sections.all()},
    )


@content_required
def province_section_form(request, section_id=None, page_id=None):
    instance = get_object_or_404(ProvincePageSection, pk=section_id) if section_id else None
    initial = {"page": page_id} if page_id else None
    page_pk = instance.page_id if instance else page_id
    return _form_response(
        request,
        form_class=ProvincePageSectionForm,
        instance=instance,
        initial=initial,
        title="Edit province section" if instance else "Add province section",
        back_url=reverse("tour:operations:content_province_sections", args=(page_pk,)),
        success_message="Province section saved.",
    )


@content_required
def province_section_delete(request, section_id):
    section = get_object_or_404(ProvincePageSection, pk=section_id)
    return _delete_response(
        request,
        obj=section,
        title="Delete province section",
        back_url=reverse("tour:operations:content_province_sections", args=(section.page_id,)),
    )


@content_required
def media_list(request):
    queryset = ManagedMedia.objects.all()
    category = request.GET.get("category", "").strip()
    if category:
        queryset = queryset.filter(category=category)
    page_obj = Paginator(queryset, 30).get_page(request.GET.get("page"))
    return render(
        request,
        "operations/content/media_list.html",
        {"page_obj": page_obj, "media_items": page_obj.object_list, "category": category},
    )


@content_required
def media_form(request, media_id=None):
    instance = get_object_or_404(ManagedMedia, pk=media_id) if media_id else None
    return _form_response(
        request,
        form_class=ManagedMediaForm,
        instance=instance,
        title="Edit media" if instance else "Upload media",
        back_url=reverse("tour:operations:content_media_list"),
        success_message="Media saved.",
    )


@content_required
def media_delete(request, media_id):
    media = get_object_or_404(ManagedMedia, pk=media_id)
    back_url = reverse("tour:operations:content_media_list")
    if request.method == "POST":
        stored_file = media.file
        _log_action(request, media, DELETION, f"Deleted {media}.")
        media.delete()
        if stored_file:
            stored_file.delete(save=False)
        messages.success(request, "Media record and stored file were deleted.")
        return redirect(back_url)
    return render(
        request,
        "operations/content/confirm_delete.html",
        {"object": media, "title": "Delete media record and file", "back_url": back_url},
    )


def _thing_config(kind):
    config = THING_TYPES.get(kind)
    if not config:
        raise PermissionDenied
    return config


@content_required
def thing_list(request, kind):
    config = _thing_config(kind)
    queryset = config["model"].objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(location__icontains=query))
    page_obj = Paginator(queryset.order_by("title"), 25).get_page(request.GET.get("page"))
    return render(
        request,
        "operations/content/thing_list.html",
        {"kind": kind, "config": config, "page_obj": page_obj, "records": page_obj.object_list, "query": query},
    )


@content_required
def thing_form(request, kind, record_id=None):
    config = _thing_config(kind)
    instance = get_object_or_404(config["model"], pk=record_id) if record_id else None
    return _form_response(
        request,
        form_class=config["form"],
        instance=instance,
        title=f"Edit {config['title']}" if instance else f"Add {config['title']}",
        back_url=reverse("tour:operations:content_thing_list", args=(kind,)),
        success_message=f"{config['title']} record saved.",
    )


@content_required
def thing_delete(request, kind, record_id):
    config = _thing_config(kind)
    return _delete_response(
        request,
        obj=get_object_or_404(config["model"], pk=record_id),
        title=f"Delete {config['title']} record",
        back_url=reverse("tour:operations:content_thing_list", args=(kind,)),
    )


@content_required
def tour_content_list(request):
    tours = (
        Tour.objects.select_related("category")
        .annotate(itinerary_count=Count("itinerary_items"))
        .order_by("-created_at")
    )
    return render(request, "operations/content/tour_list.html", {"tours": tours})


def _tour_readiness(tour):
    if not tour or not tour.pk:
        return {"checks": [], "complete": False, "itinerary_count": 0}
    itinerary_count = tour.itinerary_items.count()
    try:
        duration_days = int(tour.duration_day or 0)
    except (TypeError, ValueError):
        duration_days = 0
    has_schedule = tour.type != "schedule" or bool(tour.start_date and tour.end_date)
    checks = [
        {"label": "Cover image", "done": bool(tour.image)},
        {"label": "Destination", "done": bool(tour.location)},
        {"label": "Duration", "done": duration_days > 0},
        {"label": "Price or enquiry", "done": bool(tour.price and tour.price > 0) or tour.is_price_on_request},
        {"label": "Scheduled dates", "done": has_schedule},
        {"label": "Itinerary days", "done": itinerary_count > 0},
        {
            "label": "Duration matches itinerary",
            "done": duration_days > 0 and itinerary_count == duration_days,
        },
    ]
    return {
        "checks": checks,
        "complete": all(check["done"] for check in checks),
        "itinerary_count": itinerary_count,
    }


@content_required
def tour_content_form(request, tour_id=None):
    instance = get_object_or_404(Tour, pk=tour_id) if tour_id else None
    action = request.POST.get("action", "continue") if request.method == "POST" else ""
    publish = action == "publish"
    if request.method == "POST":
        form = TourWebsiteContentForm(
            request.POST,
            request.FILES,
            instance=instance,
            publish=publish,
        )
        if form.is_valid():
            created = instance is None
            tour = form.save(commit=False)
            if publish:
                tour.available = True
            elif action == "draft":
                tour.available = False
            else:
                tour.available = instance.available if instance else False
            tour.save()
            form.save_homepage_feature(tour)
            _log_action(
                request,
                tour,
                ADDITION if created else CHANGE,
                "Tour created as a draft." if created else "Tour website content updated.",
            )
            if publish:
                messages.success(request, "Tour published successfully.")
            elif action == "draft":
                messages.success(request, "Tour saved as a draft and hidden from the public website.")
            else:
                messages.success(request, "Tour draft saved. Add the day-by-day itinerary below.")

            if created and action == "draft":
                return redirect("tour:operations:content_tour_list")
            edit_url = reverse("tour:operations:content_tour_edit", args=(tour.pk,))
            if created:
                return redirect(f"{edit_url}#itinerary")
            return redirect(edit_url)
        messages.error(request, "Please correct the highlighted tour fields.")
    else:
        form = TourWebsiteContentForm(instance=instance)

    itinerary_items = []
    if instance:
        itinerary_items = instance.itinerary_items.select_related(
            "transport",
            "accommodation",
            "meals",
            "logistics",
            "tour_guide",
        )
    return render(
        request,
        "operations/content/tour_form.html",
        {
            "form": form,
            "tour": instance,
            "itinerary_items": itinerary_items,
            "readiness": _tour_readiness(instance),
            "back_url": reverse("tour:operations:content_tour_list"),
        },
    )


@content_required
def itinerary_content_form(request, tour_id, itinerary_id=None):
    tour = get_object_or_404(Tour, pk=tour_id)
    next_day_number = (tour.itinerary_items.aggregate(max_day=Max("day_number"))["max_day"] or 0) + 1
    item = None
    if itinerary_id is not None:
        item = get_object_or_404(ItineraryItem, pk=itinerary_id, tour=tour)
    if request.method == "POST":
        form = ItineraryItemContentForm(
            request.POST,
            request.FILES,
            instance=item,
            tour=tour,
        )
        if form.is_valid():
            created = item is None
            day_number = next_day_number if created else item.day_number
            item = form.save_for_tour(day_number)
            _log_action(
                request,
                item,
                ADDITION if created else CHANGE,
                f"Itinerary day {item.day_number} saved for {tour}.",
            )
            messages.success(request, f"Itinerary day {item.day_number} saved.")
            return redirect(
                f"{reverse('tour:operations:content_tour_edit', args=(tour.pk,))}#itinerary"
            )
        messages.error(request, "Please correct the highlighted itinerary fields.")
    else:
        form = ItineraryItemContentForm(instance=item, tour=tour)
    return render(
        request,
        "operations/content/itinerary_form.html",
        {
            "form": form,
            "tour": tour,
            "item": item,
            "day_number": item.day_number if item else next_day_number,
            "back_url": f"{reverse('tour:operations:content_tour_edit', args=(tour.pk,))}#itinerary",
        },
    )


def _resequence_itinerary(tour):
    for day_number, item in enumerate(tour.itinerary_items.order_by("day_number", "pk"), start=1):
        if item.day_number != day_number:
            ItineraryItem.objects.filter(pk=item.pk).update(day_number=day_number)


@content_required
def itinerary_content_delete(request, tour_id, itinerary_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    item = get_object_or_404(ItineraryItem, pk=itinerary_id, tour=tour)
    back_url = f"{reverse('tour:operations:content_tour_edit', args=(tour.pk,))}#itinerary"
    if request.method == "POST":
        day_number = item.day_number
        stored_image = item.image
        with transaction.atomic():
            _log_action(request, item, DELETION, f"Deleted itinerary day {day_number} from {tour}.")
            item.delete()
            _resequence_itinerary(tour)
        if stored_image:
            stored_image.delete(save=False)
        messages.success(request, f"Itinerary day {day_number} deleted.")
        return redirect(back_url)
    return render(
        request,
        "operations/content/confirm_delete.html",
        {
            "object": item,
            "title": f"Delete itinerary day {item.day_number}",
            "back_url": back_url,
        },
    )


@content_required
@require_POST
def itinerary_content_order(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    raw_ids = request.POST.getlist("day_order")
    try:
        ordered_ids = [int(item_id) for item_id in raw_ids]
    except (TypeError, ValueError):
        ordered_ids = []
    existing_ids = list(tour.itinerary_items.values_list("pk", flat=True))
    if len(ordered_ids) != len(set(ordered_ids)) or set(ordered_ids) != set(existing_ids):
        messages.error(request, "The itinerary order could not be verified. Refresh and try again.")
    else:
        with transaction.atomic():
            temporary_start = len(ordered_ids) + 1000
            for offset, item_id in enumerate(ordered_ids):
                ItineraryItem.objects.filter(pk=item_id, tour=tour).update(
                    day_number=temporary_start + offset
                )
            for day_number, item_id in enumerate(ordered_ids, start=1):
                ItineraryItem.objects.filter(pk=item_id, tour=tour).update(day_number=day_number)
        _log_action(request, tour, CHANGE, "Itinerary days reordered.")
        messages.success(request, "Itinerary order saved.")
    return redirect(
        f"{reverse('tour:operations:content_tour_edit', args=(tour.pk,))}#itinerary"
    )


@content_required
def tour_content_delete(request, tour_id):
    return _delete_response(
        request,
        obj=get_object_or_404(Tour, pk=tour_id),
        title="Delete tour",
        back_url=reverse("tour:operations:content_tour_list"),
    )


@content_required
def category_list(request):
    categories = TourCategory.objects.annotate(tour_count=Count("tours")).order_by("name")
    return render(request, "operations/content/category_list.html", {"categories": categories})


@content_required
def category_form(request, category_id=None):
    instance = get_object_or_404(TourCategory, pk=category_id) if category_id else None
    return _form_response(
        request,
        form_class=TourCategoryContentForm,
        instance=instance,
        title="Edit tour category" if instance else "Add tour category",
        back_url=reverse("tour:operations:content_category_list"),
        success_message="Tour category saved.",
    )


@content_required
def category_delete(request, category_id):
    category = get_object_or_404(TourCategory, pk=category_id)
    if category.tours.exists():
        messages.error(request, "Move or delete the tours in this category before deleting it.")
        return redirect("tour:operations:content_category_list")
    return _delete_response(
        request,
        obj=category,
        title="Delete tour category",
        back_url=reverse("tour:operations:content_category_list"),
    )
