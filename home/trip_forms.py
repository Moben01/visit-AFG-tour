from django import forms
from django.forms import BaseFormSet, formset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import EntryPlan, PopularPlace, TripPreference, TripRequest


class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            css_class = "aa-trip-input"
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "aa-trip-check"
            elif isinstance(field.widget, forms.RadioSelect):
                css_class = "aa-trip-radio"
            field.widget.attrs.setdefault("class", css_class)


class TripRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TripRequest
        fields = (
            "full_name",
            "email",
            "phone",
            "country_of_origin",
            "start_date",
            "end_date",
            "adults",
            "children",
            "budget_tier",
            "estimated_budget",
            "pace",
            "notes",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "estimated_budget": forms.NumberInput(attrs={"min": 0, "step": "1"}),
        }
        labels = {
            "estimated_budget": _("Approximate total budget (USD)"),
            "country_of_origin": _("Country or city of origin"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adults"].widget.attrs.update({"min": 1, "max": 20})
        self.fields["children"].widget.attrs.update({"min": 0, "max": 20})
        self.fields["start_date"].widget.attrs["min"] = timezone.localdate().isoformat()
        self.fields["estimated_budget"].required = False
        self.fields["notes"].required = False
        self.apply_styles()

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        adults = cleaned.get("adults") or 0
        children = cleaned.get("children") or 0
        if start and end and end < start:
            self.add_error("end_date", _("End date cannot be before start date."))
        if start and end and (end - start).days > 90:
            self.add_error("end_date", _("A custom route can contain at most 90 travel days."))
        if adults < 1:
            self.add_error("adults", _("At least one adult traveller is required."))
        if adults + children > 20:
            self.add_error("children", _("A route request can contain at most 20 travellers."))
        return cleaned


class EntryPlanForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = EntryPlan
        fields = (
            "selection_mode",
            "transport_mode",
            "arrival_origin",
            "selected_entry_point",
            "other_entry_point",
        )
        widgets = {
            "selection_mode": forms.RadioSelect,
        }
        labels = {
            "arrival_origin": _("Where will you arrive from?"),
            "selected_entry_point": _("Preferred entry point"),
            "other_entry_point": _("Other entry point"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["selected_entry_point"].required = False
        self.fields["other_entry_point"].required = False
        self.apply_styles()

    def clean(self):
        cleaned = super().clean()
        selection_mode = cleaned.get("selection_mode")
        selected_entry_point = cleaned.get("selected_entry_point")
        other_entry_point = (cleaned.get("other_entry_point") or "").strip()
        if selection_mode == "self" and not selected_entry_point:
            self.add_error("selected_entry_point", _("Select your entry point or ask us to recommend one."))
        if selection_mode == "self" and selected_entry_point == "other" and not other_entry_point:
            self.add_error("other_entry_point", _("Describe the entry point you plan to use."))
        return cleaned


class TripPreferenceForm(StyledFormMixin, forms.ModelForm):
    INTEREST_CHOICES = (
        ("culture", _("Culture and heritage")),
        ("history", _("History and architecture")),
        ("nature", _("Nature and landscapes")),
        ("food", _("Food and local life")),
        ("photography", _("Photography")),
        ("adventure", _("Adventure")),
        ("community", _("Community experiences")),
    )
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = TripPreference
        fields = (
            "interests",
            "accommodation_type",
            "transport_preference",
            "needs_local_guide",
            "needs_translator",
            "accessibility_notes",
        )
        widgets = {
            "accessibility_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()


class TripStopInputForm(StyledFormMixin, forms.Form):
    position = forms.IntegerField(min_value=1, required=False, widget=forms.HiddenInput)
    destination = forms.ModelChoiceField(
        queryset=PopularPlace.objects.none(),
        empty_label=_("Choose a province"),
    )
    nights = forms.IntegerField(min_value=1, max_value=30, initial=1)
    notes = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Optional priorities for this stop")}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["destination"].queryset = PopularPlace.objects.filter(is_active=True)
        self.apply_styles()


class BaseTripStopFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        destinations = []
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or form.cleaned_data.get("DELETE"):
                continue
            destination = form.cleaned_data.get("destination")
            if destination:
                destinations.append(destination.pk)
        if not destinations:
            raise forms.ValidationError(_("Choose at least one province for the route."))
        if len(destinations) != len(set(destinations)):
            raise forms.ValidationError(_("Each province can appear only once in a route."))


TripStopFormSet = formset_factory(
    TripStopInputForm,
    formset=BaseTripStopFormSet,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
    max_num=12,
    validate_max=True,
)
