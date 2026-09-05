import re
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.text import slugify
User = get_user_model()

class TourCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=120000)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Translator(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),   
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=False)
    email = models.EmailField(blank=False)
    languages = models.ManyToManyField('Languages', blank=True)
    experience_years = models.PositiveIntegerField()
    certifications = models.TextField(blank=True, help_text="Translation certificates or qualifications")
    bio = models.TextField(blank=True)
    id_number = models.CharField(max_length=50, blank=False, help_text="For verification (optional)")
    cv = models.FileField(upload_to='translators/cv/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='translators/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField()
    is_approved = models.BooleanField(default=False, help_text="Checked and approved by admin")
    is_active = models.BooleanField(default=True, help_text="Can appear publicly on the website")

    def __str__(self):
        return self.name


class TourGuide(models.Model):
    SPECIALTY_CHOICES = [
        ('cultural', 'Cultural Tours'),
        ('historical', 'Historical Tours'),
        ('adventure', 'Adventure & Trekking'),
        ('nature', 'Nature & Wildlife'),
        ('religious', 'Religious & Pilgrimage Tours'),
        ('city', 'City & Walking Tours'),
        ('archaeology', 'Archaeological Sites'),
        ('language', 'Language Interpretation'),
        ('photography', 'Photography Tours'),
        ('custom', 'Custom / Private Tours'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    provinces = models.CharField(max_length=200, help_text="City or region based in")
    languages = models.CharField(max_length=200, help_text="e.g. English, Pashto, Chinese")
    experience_years = models.PositiveIntegerField()
    specialties = MultiSelectField(
        choices=SPECIALTY_CHOICES,
        
        max_length=200,
        help_text="Select the types of tours you specialize in"
    )
   
    bio = models.TextField(blank=True)
    id_number = models.CharField(
        max_length=50,
        help_text="National ID or Passport Number"
    )
    certifications = models.TextField(
        blank=True,
        help_text="Any certifications or training in guiding or tourism"
    )
    cv = models.FileField(upload_to='guides/cv/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='guides/', blank=True, null=True)
    is_approved = models.BooleanField(default=False, help_text="Approved by admin")
    is_active = models.BooleanField(default=True, help_text="Visible on the website")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SecurityGuard(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    experience_years = models.PositiveIntegerField()
    languages = models.ManyToManyField('Languages', blank=True)  # Optional if they communicate with clients
    certifications = models.TextField(blank=True, help_text="Security training or licenses")
    location = models.CharField(max_length=100, help_text="City or area they operate in")
    
    availability = models.BooleanField(default=True)
    daily_rate = models.FloatField(help_text="Price per day in USD")
    total_price = models.FloatField()
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='security_guards/', blank=True, null=True)

    id_document = models.FileField(upload_to='security_guards/ids/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="Verified by admin")

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"


class EntryTicket(models.Model):
    TICKET_STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entry_tickets')
    ticket_number = models.CharField(max_length=20, unique=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='booked')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Ticket {self.ticket_number} for {self.user.username}'

    class Meta:
        ordering = ['-booking_date']

class Permit(models.Model):
    PERMIT_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permits')
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PERMIT_STATUS, default='pending')
    document = models.FileField(upload_to='permits/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Permit for {self.user.username} - {self.status}'

class Tour(models.Model):
    SCHEDULE_OR_NOT = [
        ('schedule', 'schedule'),
        ('not_schedule', 'not_schedule'),
    ]
    PROVINCE_CHOICES = [
        ('Badakhshan', 'Badakhshan'), ('Badghis', 'Badghis'), ('Baghlan', 'Baghlan'),
        ('Balkh', 'Balkh'), ('Bamyan', 'Bamyan'), ('Daykundi', 'Daykundi'),
        ('Farah', 'Farah'), ('Faryab', 'Faryab'), ('Ghazni', 'Ghazni'),
        ('Ghor', 'Ghor'), ('Helmand', 'Helmand'), ('Herat', 'Herat'),
        ('Jowzjan', 'Jowzjan'), ('Kabul', 'Kabul'), ('Kandahar', 'Kandahar'),
        ('Kapisa', 'Kapisa'), ('Khost', 'Khost'), ('Kunar', 'Kunar'),
        ('Kunduz', 'Kunduz'), ('Laghman', 'Laghman'), ('Logar', 'Logar'),
        ('Nangarhar', 'Nangarhar'), ('Nimroz', 'Nimroz'), ('Nuristan', 'Nuristan'),
        ('Paktia', 'Paktia'), ('Paktika', 'Paktika'), ('Panjshir', 'Panjshir'),
        ('Parwan', 'Parwan'), ('Samangan', 'Samangan'), ('Sar-e Pol', 'Sar-e Pol'),
        ('Takhar', 'Takhar'), ('Urozgan', 'Urozgan'), ('Wardak', 'Wardak'),
        ('Zabul', 'Zabul'),
    ]
    category = models.ForeignKey(TourCategory, on_delete=models.CASCADE, related_name='tours')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='tour-image/', blank=True)
    slug = models.SlugField(unique=True, blank=True)
    type = models.CharField(max_length=120, choices=SCHEDULE_OR_NOT)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()
    location = MultiSelectField(
        choices=PROVINCE_CHOICES,
        max_choices=34,
        max_length=400,
        blank=True,
    )
    duration_day = models.CharField(max_length=150, blank=True, default='')
    duration_night = models.CharField(max_length=150, blank=True, default='')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    available = models.BooleanField(default=False)
    google_location = models.CharField(max_length=2000000, blank=True, default='')
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, null=True, blank=True)
    security_gard = models.ForeignKey(SecurityGuard, on_delete=models.SET_NULL, null=True, blank=True)
    translator = models.ForeignKey(Translator, on_delete=models.SET_NULL, null=True, blank=True)
    entry_ticket = models.ForeignKey(EntryTicket, on_delete=models.SET_NULL, null=True, blank=True, related_name="entry_tickets")
    permit = models.ForeignKey(Permit, on_delete=models.SET_NULL, null=True, blank=True, related_name="permits")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_price_on_request(self):
        return self.price is None or self.price <= 0

    def _generate_unique_slug(self):
        base = slugify(self.title)[:180] or f'tour-{uuid.uuid4().hex[:8]}'
        candidate = base
        suffix = 2
        queryset = type(self).objects.exclude(pk=self.pk)
        while queryset.filter(slug=candidate).exists():
            suffix_text = f'-{suffix}'
            candidate = f'{base[:200 - len(suffix_text)]}{suffix_text}'
            suffix += 1
        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tour_detail', args=[self.slug])



class User_favorite_tour(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    favorite = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Yes" if self.favorite else "No"
        return f"{self.user} - Favorite '{self.tour}': {status}"


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/')


class Booking(models.Model):
    BOOKING_SIT = [
        ('Booked', 'Booked'),
        ('in_progress', 'in_progress'),
        ('upcoming', 'upcoming'),
        ('completed', 'completed'),
        ('Cancelled', 'Cancelled'),
        ('Reviewed', 'Reviewed'),
       
    ]

    tour = models.ForeignKey('Tour', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booked_tours')
    booking_date = models.DateField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    situation = models.CharField(max_length=20, choices=BOOKING_SIT, default='upcoming')

    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    paid = models.BooleanField(default=False)
    paid_amount = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} booked {self.tour} on {self.booking_date.strftime('%Y-%m-%d')}"


class Accommodation(models.Model):
    ACCOMMODATION_TYPES = [
        ('hotel', 'Hotel'),
        ('hostel', 'Hostel'),
        ('guesthouse', 'Guesthouse'),
        ('camp', 'Camp'),
        ('resort', 'Resort'),
        ('homestay', 'Homestay'),
        ('apartment', 'Apartment'),
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ACCOMMODATION_TYPES)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    )    
    price_per_night = models.FloatField()
    total_price = models.FloatField(default=0)
    image = models.ImageField(upload_to='accommodation_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transport(models.Model):
    TRANSPORT_TYPES = [
        ('bus', 'Bus'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('train', 'Train'),
        ('flight', 'Flight'),
        ('boat', 'Boat'),
        ('bike', 'Bike'),
        ('walking', 'Walking'),
    ]
    type = models.CharField(max_length=20, choices=TRANSPORT_TYPES)
    company_name = models.CharField(max_length=100, blank=True)
    total_price = models.FloatField(default=0)
    description = models.TextField(blank=True)
    vehicle_number = models.CharField(max_length=50, blank=True)
    seats_available = models.PositiveIntegerField(null=True, blank=True)
    departure_location = models.CharField(max_length=255)
    arrival_location = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    image = models.ImageField(upload_to='transport_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return f"Type '{self.type}' - C-Name '{self.company_name}"
    # Format type and company name neatly, omit company name if empty
        if self.company_name:
            return f"{self.get_type_display()} - {self.company_name}"
        return self.get_type_display()


class Meal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.meal_type.capitalize()} on {self.itinerary_item}'


class Logistic(models.Model):
    TRANSPORT_MODE_CHOICES = [
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('plane', 'Plane'),
        ('train', 'Train'),
        ('boat', 'Boat'),
        ('walking', 'Walking'),
        ('other', 'Other'),
    ]
    mode_of_transport = models.CharField(max_length=50, choices=TRANSPORT_MODE_CHOICES)
    departure_time = models.TimeField(blank=True, null=True)
    arrival_time = models.TimeField(blank=True, null=True)
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.mode_of_transport.capitalize()} from {self.from_location} to {self.to_location}'

class ItineraryItem(models.Model):
    TRANSPORT_TYPE = [
        ('Airplane', 'Airplane'),
        ('Car', 'Car'),
        ('Bus', 'Bus'),
        ('Van', 'Van'),
        ('Train', 'Train'),
        ('Boat', 'Boat'),
        ('Bike', 'Bike'),
        ('Walking', 'Walking'),
        ('Other', 'Other'),
    ]
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary_items')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    date = models.DateTimeField()
    image = models.ImageField(upload_to='itenary-images', blank=True)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.SET_NULL, blank=True, null=True)
    type_of_transport = models.CharField(
        max_length=120,
        choices=TRANSPORT_TYPE,
        blank=True,
    )
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, blank=True, null=True)
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, blank=True, null=True)
    meals = models.ForeignKey(Meal, on_delete=models.SET_NULL, blank=True, null=True)
    logistics = models.ForeignKey(Logistic, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number} - {self.title or 'Itinerary'} - {self.tour}"

    @property
    def is_customized(self):
        return False

class UserItineraryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary_items_new')
    itinerary_item = models.ForeignKey(ItineraryItem, on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    date = models.DateTimeField()
    image = models.ImageField(upload_to = 'itenary-images')
    accommodation = models.ForeignKey(Accommodation, on_delete=models.SET_NULL, blank=True, null=True)
    type_of_transport = models.CharField(max_length=120)
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, blank=True, null=True)
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, blank=True, null=True)
    meals = models.ForeignKey(Meal, on_delete=models.SET_NULL, blank=True, null=True)
    logistics = models.ForeignKey(Logistic, on_delete=models.SET_NULL, blank=True, null=True)
    customized_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number} - {self.title or 'Itinerary'} - {self.tour}"

    @property
    def is_customized(self):
        return True

class Frequently_asked_questions(models.Model):
    tour_id = models.ForeignKey(Tour, on_delete=models.CASCADE)
    question = models.CharField(max_length=30000)
    answer = models.TextField()
    data_bs_target = models.CharField(max_length=200)


class EnquireUs(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True, blank=True, help_text="Optional - the tour user is enquiring about")
    date_created = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"Enquiry from {self.full_name} - {self.subject[:30]}"


    
class Includes(models.Model):
    tour =models.ForeignKey(Tour, on_delete=models.CASCADE)
    title =models.CharField(max_length=500)

    
class Excludes(models.Model):
    tour =models.ForeignKey(Tour, on_delete=models.CASCADE)
    title =models.CharField(max_length=500)

class Ready_tour_for_booking(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user',)  # Optional: only allow 1 active per user

    def __str__(self):
        return f"{self.user.username} is preparing to book {self.tour.title}"


class Languages(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=100)
    total_price = models.FloatField()

    def __str__(self):
        return f"language {self.name} | code {self.code}"


class TourGuideInterest(models.Model):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name='guide_interests')
    guide = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interested_tours')
    message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    is_shortlisted = models.BooleanField(default=False)  # ✅ multiple can be True
    is_selected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tour', 'guide')  # Prevent duplicate applications

    def __str__(self):
        return f"{self.guide.username} → {self.tour.title}"


class TourGuideAssignment(models.Model):
    URGENCY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Emergency', 'Emergency'),
    ]

    tour = models.OneToOneField('Tour', on_delete=models.CASCADE, related_name='assigned_guide')
    assigned_at = models.DateTimeField(auto_now_add=True)
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='Normal')
    bonus_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # ✅ for urgent/emergency cases
    note = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Guide {self.tour.title} assigned to {self.tour.title}"



class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='accommodation_gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.accommodation.name}"


class TransportImage(models.Model):
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='transport_gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.transport}"
    




class PreArrivalRequirement(models.Model):
    VISA_STATUS_CHOICES = [
        ('yes', 'Yes, I have the visa'),
        ('no', 'No, I need an invitation letter'),
    ]

    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='pre_arrival_tour')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pre_arrival_forms_tour')

    # Visa-related fields
    visa_status = models.CharField(max_length=10, choices=VISA_STATUS_CHOICES)
    visa_copy = models.FileField(upload_to='visa_copies/', blank=True, null=True)

    # Passport
    passport_copy = models.FileField(upload_to='passport_copies/', blank=True, null=True)

    # Travel details
    travel_start_date = models.DateField(blank=True, null=True)
    travel_end_date = models.DateField(blank=True, null=True)
    embassy_location = models.CharField(max_length=255, blank=True, null=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=25, blank=True, null=True)
    emergency_contact_email = models.EmailField(blank=True, null=True)

    # Insurance
    has_insurance = models.BooleanField(default=False)
    insurance_copy = models.FileField(upload_to='insurance_docs/', blank=True, null=True)

    invitation_letter = models.FileField(upload_to='insurance_docs/', blank=True, null=True)

    # Medical info
    has_medical_conditions = models.BooleanField(default=False)
    medical_notes = models.TextField(blank=True)

    # SIM / Communication
    needs_afghan_sim = models.BooleanField(default=False)

    # Acknowledgment
    safety_guideline_accepted = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pre-Arrival for {self.user.get_full_name()} - {self.booking.tour.title}"



    

class PreArrival(models.Model):
    ENTRY_POINTS = [
        ('kabul_airport', 'Kabul International Airport'),
        ('herat_airport', 'Herat International Airport'),
        ('mazar_airport', 'Mazar-i-Sharif Airport'),
        ('kandahar_airport', 'Kandahar Airport'),
        ('torkham_border', 'Torkham Border (Pakistan)'),
        ('spin_boldak', 'Spin Boldak (Pakistan)'),
        ('islam_qala', 'Islam Qala (Iran)'),
        ('hairatan', 'Hairatan (Uzbekistan)'),
        ('torghundi', 'Torghundi (Turkmenistan)'),
        ('other', 'Other'),
    ]


   

    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='pre_arrival')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pre_arrival_forms')

    # Visa status + required docs
    passport_copy = models.FileField(upload_to='pre_arrival/passport/', blank=False, null=False)
    visa_copy = models.FileField(upload_to='pre_arrival/visa/', blank=True, null=True)
    
    # Flight details
    flight_ticket = models.FileField(upload_to='pre_arrival/flight/', blank=False, null=False)
    flight_date = models.DateField(blank=False, null=False)
    flight_time = models.TimeField(blank=False, null=False)
    airline_name = models.CharField(max_length=100, blank=True, help_text="Optional: Airline name or flight number")
    flight_number = models.CharField(max_length=50, blank=True, help_text="Optional: Flight number if available")
    entry_point = models.CharField(max_length=50, choices=ENTRY_POINTS, help_text="Where will you enter Afghanistan?")
    entry_point_other = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="If 'Other', please specify"
    )
    # Emergency info
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_email = models.EmailField(blank=True, null=True)
    # Health info
    has_medical_conditions = models.BooleanField(default=False)
    medical_details = models.TextField(blank=True, help_text="List any allergies or chronic conditions.")

    # Travel preferences

    # Safety acknowledgment
    safety_acknowledgement = models.BooleanField(default=False, help_text="Confirm that you have read and accepted the safety guidelines.")

    # Optional notes
    additional_notes = models.TextField(blank=True, help_text="Anything else you'd like us to know before arrival.")

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pre-Arrival · {self.booking} ({self.user})"
    















class Driver(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    photo = models.ImageField(upload_to='pickup/driver/', blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=120, blank=True)  # e.g. "Dari, Pashto, English"
    def __str__(self): return self.name

class Operator(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    photo = models.ImageField(upload_to='pickup/operator/', blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=120, blank=True)
    def __str__(self): return self.name

class Vehicle(models.Model):
    title = models.CharField(max_length=120)  # e.g., "Land Cruiser"
    plate_no = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveIntegerField(default=4)
    photo = models.ImageField(upload_to='pickup/vehicle/', blank=True, null=True)
    color = models.CharField(max_length=50, blank=True)
    def __str__(self): return f"{self.title} {self.plate_no or ''}".strip()

class PickupPlan(models.Model):
    STATUS = [
        ('scheduled', 'Scheduled'),
        ('on_route', 'On Route'),
        ('waiting', 'Waiting at Point'),
        ('picked_up', 'Picked Up'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ]
    TYPE = [('airport','Airport'), ('border','Land Border'), ('hotel','Hotel/Other')]

    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='pickup')

    # context (from PreArrival snapshot)
    pickup_type = models.CharField(max_length=20, choices=TYPE, default='airport')
    entry_point_label = models.CharField(max_length=120)
    entry_point_code = models.CharField(max_length=50, blank=True)

    scheduled_at = models.DateTimeField()
    window_minutes = models.PositiveIntegerField(default=60)

    # crew
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL)
    operator = models.ForeignKey(Operator, null=True, blank=True, on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.SET_NULL)

    # contact details shown to tourist (can override)
    driver_phone_share = models.CharField(max_length=30, blank=True)
    operator_phone_share = models.CharField(max_length=30, blank=True)
    tourist_phone_share = models.CharField(max_length=30, blank=True)

    # meeting guidance
    meeting_point = models.CharField(max_length=255, blank=True)     # "Arrival Gate A – Exit 2"
    meeting_note = models.TextField(blank=True)                      # signage text, what to look for
    welcome_note = models.CharField(max_length=255, blank=True)      # short greeting for tourist

    # tourist-facing visibility
    visible_to_tourist = models.BooleanField(default=True)

    # ops tracking
    status = models.CharField(max_length=20, choices=STATUS, default='scheduled')
    otp_code = models.CharField(max_length=8, blank=True)
    checkin_photo = models.ImageField(upload_to='pickup/proofs/', blank=True, null=True)
    picked_up_at = models.DateTimeField(blank=True, null=True)
    no_show_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f"Pickup · {self.booking_id} · {self.entry_point_label}"













class GiftItem(models.Model):
    """List of possible gifts (dynamic, admin-manageable)."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='gifts/photos/', blank=True, null=True)
    is_afghan_special = models.BooleanField(default=False, help_text="Mark if this is an Afghan cultural gift")

    def __str__(self):
        return self.name


class WelcomePackage(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='welcome_package')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='welcome_packages')

    # Generic welcome items
    welcome_letter = models.BooleanField(default=False)
    sim_card = models.BooleanField(default=False)
    printed_itinerary = models.BooleanField(default=False)
    local_map = models.BooleanField(default=False)
    emergency_numbers_card = models.BooleanField(default=False)

    # Dynamic gift selection
    gifts = models.ManyToManyField(GiftItem, blank=True, related_name="welcome_packages")

    package_photo = models.ImageField(upload_to='welcome_packages/photos/', blank=True, null=True)
    special_notes = models.TextField(blank=True, help_text="Any special items or notes for this tourist.")
    prepared_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Welcome Package for {self.user} - {self.booking.tour.title}"


# Tour workforce, supplier, and contract management.


class EmployeeProfile(models.Model):
    EMPLOYMENT_TYPES = [
        ('permanent', 'Permanent'), ('fixed_term', 'Fixed term'), ('part_time', 'Part time'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_code = models.CharField(max_length=40, unique=True, blank=True, null=True)
    department = models.CharField(max_length=120)
    job_title = models.CharField(max_length=120)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='permanent')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='direct_reports')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    emergency_contact = models.CharField(max_length=180, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before start date.'})

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} · {self.job_title}"


class CrewRole(models.Model):
    code = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    requires_training = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class CrewMember(models.Model):
    VERIFICATION_STATUS = [
        ('draft', 'Draft'), ('submitted', 'Submitted'), ('under_review', 'Under review'),
        ('interview', 'Interview required'), ('training', 'Training required'),
        ('approved', 'Approved'), ('needs_update', 'Needs update'),
        ('suspended', 'Suspended'), ('rejected', 'Rejected'), ('expired', 'Documents expired'),
    ]
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other / prefer not to say')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='crew_profile')
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    display_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    base_location = models.CharField(max_length=180)
    service_regions = models.TextField(blank=True, help_text='Provinces or regions where this person can work.')
    languages = models.CharField(max_length=300, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='crew/profiles/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='draft')
    available_for_work = models.BooleanField(default=True)
    default_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    preferred_currency = models.CharField(max_length=3, default='USD')
    emergency_contact_name = models.CharField(max_length=160, blank=True)
    emergency_contact_phone = models.CharField(max_length=40, blank=True)
    payout_method = models.CharField(max_length=80, blank=True)
    payout_reference = models.CharField(max_length=180, blank=True)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    completed_assignments = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_crew_members')
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    roles = models.ManyToManyField(CrewRole, through='CrewQualification', related_name='crew_members')

    class Meta:
        ordering = ('display_name',)

    @property
    def is_approved(self):
        return self.verification_status == 'approved'

    def __str__(self):
        return self.display_name


class CrewQualification(models.Model):
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='qualifications')
    role = models.ForeignKey(CrewRole, on_delete=models.PROTECT, related_name='qualifications')
    experience_years = models.PositiveIntegerField(default=0)
    specialties = models.CharField(max_length=300, blank=True)
    usual_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('crew', 'role'), name='unique_crew_role')]

    def __str__(self):
        return f"{self.crew} · {self.role}"


class CrewDocument(models.Model):
    DOCUMENT_TYPES = [
        ('identity', 'Identity document'), ('passport', 'Passport'), ('cv', 'CV'),
        ('certificate', 'Certificate'), ('license', 'Professional license'),
        ('background', 'Background check'), ('other', 'Other'),
    ]
    REVIEW_STATUS = [('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')]
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to='crew/documents/')
    reference_number = models.CharField(max_length=100, blank=True)
    issued_at = models.DateField(blank=True, null=True)
    expires_at = models.DateField(blank=True, null=True)
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='pending')
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_crew_documents')
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crew} · {self.title}"


class CrewAvailability(models.Model):
    AVAILABILITY_TYPES = [('available', 'Available'), ('unavailable', 'Unavailable'), ('preferred', 'Preferred')]
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='availability_blocks')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    availability_type = models.CharField(max_length=20, choices=AVAILABILITY_TYPES)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('start_at',)

    def clean(self):
        if self.end_at <= self.start_at:
            raise ValidationError({'end_at': 'End time must be after start time.'})

    def __str__(self):
        return f"{self.crew} · {self.get_availability_type_display()}"


class CrewOpportunity(models.Model):
    STATUS = [
        ('draft', 'Draft'), ('pending_approval', 'Pending approval'), ('published', 'Published'),
        ('closed', 'Applications closed'), ('shortlisting', 'Shortlisting'),
        ('offer_sent', 'Offer sent'), ('filled', 'Filled'), ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    COMPENSATION_TYPES = [
        ('fixed', 'Fixed'), ('daily', 'Daily'), ('hourly', 'Hourly'), ('negotiable', 'Negotiable'),
    ]
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='crew_opportunities')
    role = models.ForeignKey(CrewRole, on_delete=models.PROTECT, related_name='opportunities')
    title = models.CharField(max_length=200)
    summary = models.TextField()
    duties = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    positions = models.PositiveIntegerField(default=1)
    minimum_experience_years = models.PositiveIntegerField(default=0)
    required_languages = models.CharField(max_length=240, blank=True)
    compensation_type = models.CharField(max_length=20, choices=COMPENSATION_TYPES, default='fixed')
    currency = models.CharField(max_length=3, default='USD')
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    accommodation_included = models.BooleanField(default=False)
    meals_included = models.BooleanField(default=False)
    transport_included = models.BooleanField(default=False)
    application_deadline = models.DateTimeField()
    status = models.CharField(max_length=24, choices=STATUS, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_crew_opportunities')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('start_at', '-created_at')
        indexes = [models.Index(fields=('status', 'start_at'))]

    def clean(self):
        errors = {}
        if self.end_at <= self.start_at:
            errors['end_at'] = 'End time must be after start time.'
        if self.application_deadline >= self.start_at:
            errors['application_deadline'] = 'Application deadline must be before the assignment starts.'
        if self.budget_min is not None and self.budget_max is not None and self.budget_max < self.budget_min:
            errors['budget_max'] = 'Maximum budget cannot be below minimum budget.'
        if errors:
            raise ValidationError(errors)

    @property
    def is_open(self):
        return self.status == 'published' and self.application_deadline > timezone.now()

    def __str__(self):
        return f"{self.title} · {self.tour}"


class CrewApplication(models.Model):
    STATUS = [
        ('submitted', 'Submitted'), ('under_review', 'Under review'),
        ('shortlisted', 'Shortlisted'), ('interview', 'Interview scheduled'),
        ('negotiation', 'Negotiation'), ('offer_sent', 'Offer sent'),
        ('accepted', 'Accepted'), ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'), ('expired', 'Expired'),
    ]
    opportunity = models.ForeignKey(CrewOpportunity, on_delete=models.CASCADE, related_name='applications')
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField()
    relevant_experience = models.TextField(blank=True)
    proposed_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    availability_confirmed = models.BooleanField(default=False)
    terms_acknowledged = models.BooleanField(default=False)
    needs_transport = models.BooleanField(default=False)
    needs_accommodation = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default='submitted')
    internal_note = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_crew_applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-applied_at',)
        constraints = [models.UniqueConstraint(fields=('opportunity', 'crew'), name='unique_crew_application')]

    def __str__(self):
        return f"{self.crew} → {self.opportunity}"


class CrewOffer(models.Model):
    STATUS = [
        ('draft', 'Draft'), ('sent', 'Sent'), ('countered', 'Countered'),
        ('accepted', 'Accepted'), ('declined', 'Declined'), ('expired', 'Expired'),
        ('withdrawn', 'Withdrawn'),
    ]
    application = models.ForeignKey(CrewApplication, on_delete=models.CASCADE, related_name='offers')
    version = models.PositiveIntegerField(default=1)
    compensation_type = models.CharField(max_length=20, choices=CrewOpportunity.COMPENSATION_TYPES, default='fixed')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expense_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    terms = models.TextField()
    cancellation_terms = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    expires_at = models.DateTimeField()
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='sent_crew_offers')
    responded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-version',)
        constraints = [models.UniqueConstraint(fields=('application', 'version'), name='unique_application_offer_version')]

    def clean(self):
        if self.end_at <= self.start_at:
            raise ValidationError({'end_at': 'End time must be after start time.'})

    def __str__(self):
        return f"Offer v{self.version} · {self.application}"


class CrewEngagement(models.Model):
    STATUS = [
        ('pending_acceptance', 'Pending acceptance'), ('confirmed', 'Confirmed'),
        ('booked', 'Booked'), ('checked_in', 'Checked in'), ('in_progress', 'In progress'),
        ('completed', 'Completed'), ('no_show', 'No show'), ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    ACTIVE_STATUSES = ('pending_acceptance', 'confirmed', 'booked', 'checked_in', 'in_progress')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='crew_engagements')
    opportunity = models.ForeignKey(CrewOpportunity, on_delete=models.SET_NULL, blank=True, null=True, related_name='engagements')
    application = models.OneToOneField(CrewApplication, on_delete=models.SET_NULL, blank=True, null=True, related_name='engagement')
    offer = models.OneToOneField(CrewOffer, on_delete=models.SET_NULL, blank=True, null=True, related_name='engagement')
    crew = models.ForeignKey(CrewMember, on_delete=models.PROTECT, related_name='engagements')
    role = models.ForeignKey(CrewRole, on_delete=models.PROTECT, related_name='engagements')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    compensation_type = models.CharField(max_length=20, choices=CrewOpportunity.COMPENSATION_TYPES, default='fixed')
    agreed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expense_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    duties = models.TextField(blank=True)
    schedule_note = models.TextField(blank=True)
    meeting_point = models.CharField(max_length=255, blank=True)
    cancellation_terms = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=STATUS, default='confirmed')
    accepted_at = models.DateTimeField(blank=True, null=True)
    checked_in_at = models.DateTimeField(blank=True, null=True)
    checked_out_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_crew_engagements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('start_at',)
        indexes = [models.Index(fields=('crew', 'start_at', 'end_at'))]

    def clean(self):
        errors = {}
        if self.end_at <= self.start_at:
            errors['end_at'] = 'End time must be after start time.'
        if self.crew_id and self.start_at and self.end_at and self.status in self.ACTIVE_STATUSES:
            conflict = CrewEngagement.objects.filter(
                crew_id=self.crew_id, status__in=self.ACTIVE_STATUSES,
                start_at__lt=self.end_at, end_at__gt=self.start_at,
            ).exclude(pk=self.pk)
            if conflict.exists():
                errors['start_at'] = 'This crew member is already booked during the selected period.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.crew} · {self.role} · {self.tour}"


class CrewPayment(models.Model):
    STATUS = [
        ('pending', 'Pending'), ('approved', 'Approved'), ('processing', 'Processing'),
        ('paid', 'Paid'), ('failed', 'Failed'), ('disputed', 'Disputed'),
    ]
    engagement = models.OneToOneField(CrewEngagement, on_delete=models.CASCADE, related_name='payment')
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approved_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    payment_method = models.CharField(max_length=80, blank=True)
    payment_reference = models.CharField(max_length=160, blank=True)
    receipt = models.FileField(upload_to='crew/payments/', blank=True, null=True)
    note = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_crew_payments')
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_net(self):
        return self.base_amount + self.bonus_amount + self.approved_expenses - self.deductions

    def __str__(self):
        return f"Payment · {self.engagement}"


class CrewReview(models.Model):
    REVIEWER_TYPES = [('tourist', 'Tourist'), ('operations', 'Operations')]
    engagement = models.ForeignKey(CrewEngagement, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crew_reviews_given')
    reviewer_type = models.CharField(max_length=20, choices=REVIEWER_TYPES)
    professionalism = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    knowledge = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    safety = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    overall = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('engagement', 'reviewer', 'reviewer_type'), name='unique_crew_engagement_review')]

    def __str__(self):
        return f"{self.overall}/5 · {self.engagement}"


class TrainingCourse(models.Model):
    title = models.CharField(max_length=200)
    code = models.SlugField(max_length=80, unique=True)
    description = models.TextField()
    content = models.TextField(blank=True)
    required_for_roles = models.ManyToManyField(CrewRole, blank=True, related_name='training_courses')
    passing_score = models.PositiveSmallIntegerField(default=70)
    validity_months = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CrewTrainingRecord(models.Model):
    STATUS = [
        ('assigned', 'Assigned'), ('in_progress', 'In progress'),
        ('passed', 'Passed'), ('failed', 'Failed'), ('expired', 'Expired'),
    ]
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='training_records')
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='crew_records')
    status = models.CharField(max_length=20, choices=STATUS, default='assigned')
    score = models.PositiveSmallIntegerField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateField(blank=True, null=True)
    certificate = models.FileField(upload_to='crew/training/', blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_training_records')

    class Meta:
        constraints = [models.UniqueConstraint(fields=('crew', 'course'), name='unique_crew_training_course')]

    def __str__(self):
        return f"{self.crew} · {self.course}"


class CrewCase(models.Model):
    CATEGORY = [
        ('payment', 'Payment'), ('safety', 'Safety'), ('conduct', 'Conduct'),
        ('schedule', 'Schedule'), ('customer', 'Customer'), ('other', 'Other'),
    ]
    STATUS = [
        ('open', 'Open'), ('under_review', 'Under review'),
        ('waiting', 'Waiting for information'), ('resolved', 'Resolved'), ('closed', 'Closed'),
    ]
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='cases')
    engagement = models.ForeignKey(CrewEngagement, on_delete=models.SET_NULL, blank=True, null=True, related_name='cases')
    category = models.CharField(max_length=20, choices=CATEGORY)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='open')
    resolution = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_crew_cases')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_crew_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Case #{self.pk} · {self.subject}"


class CrewNotification(models.Model):
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=180)
    message = models.TextField()
    url = models.CharField(max_length=300, blank=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class SupplierCategory(models.Model):
    code = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ServiceSupplier(models.Model):
    ENTITY_TYPES = [('individual', 'Individual / sole owner'), ('company', 'Company / organization')]
    STATUS = [
        ('lead', 'Lead'), ('onboarding', 'Onboarding'), ('under_review', 'Under review'),
        ('approved', 'Approved'), ('active', 'Active'), ('suspended', 'Suspended'),
        ('expired', 'Expired'), ('terminated', 'Terminated'), ('blacklisted', 'Blacklisted'),
    ]
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='supplier_profile')
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    legal_name = models.CharField(max_length=200)
    trading_name = models.CharField(max_length=200, blank=True)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES, default='company')
    categories = models.ManyToManyField(SupplierCategory, related_name='suppliers')
    contact_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    service_regions = models.TextField(blank=True)
    business_license_number = models.CharField(max_length=120, blank=True)
    tax_number = models.CharField(max_length=120, blank=True)
    contract_email = models.EmailField(blank=True)
    payout_method = models.CharField(max_length=80, blank=True)
    payout_reference = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='onboarding')
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_suppliers')
    approved_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('legal_name',)

    @property
    def display_name(self):
        return self.trading_name or self.legal_name

    @property
    def is_approved(self):
        return self.status in {'approved', 'active'}

    def __str__(self):
        return self.display_name


class SupplierDocument(models.Model):
    DOCUMENT_TYPES = [
        ('license', 'Business license'), ('tax', 'Tax document'), ('insurance', 'Insurance'),
        ('bank', 'Bank confirmation'), ('safety', 'Safety certificate'), ('other', 'Other'),
    ]
    supplier = models.ForeignKey(ServiceSupplier, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to='suppliers/documents/')
    reference_number = models.CharField(max_length=100, blank=True)
    expires_at = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier} · {self.title}"


class SupplierService(models.Model):
    supplier = models.ForeignKey(ServiceSupplier, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(SupplierCategory, on_delete=models.PROTECT, related_name='services')
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=40, default='service')
    capacity = models.PositiveIntegerField(blank=True, null=True)
    base_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    location = models.CharField(max_length=180, blank=True)
    terms = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.supplier} · {self.name}"


class SupplierAsset(models.Model):
    ASSET_TYPES = [
        ('hotel', 'Hotel / property'), ('room', 'Room type'), ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'), ('venue', 'Venue'), ('other', 'Other'),
    ]
    supplier = models.ForeignKey(ServiceSupplier, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    name = models.CharField(max_length=180)
    reference = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    daily_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    document_expiry = models.DateField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.supplier} · {self.name}"


class SupplierContract(models.Model):
    STATUS = [
        ('draft', 'Draft'), ('negotiation', 'Negotiation'), ('pending_approval', 'Pending approval'),
        ('signed', 'Signed'), ('active', 'Active'), ('expiring', 'Expiring'),
        ('expired', 'Expired'), ('suspended', 'Suspended'), ('terminated', 'Terminated'),
    ]
    supplier = models.ForeignKey(ServiceSupplier, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    currency = models.CharField(max_length=3, default='USD')
    value_ceiling = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    payment_terms = models.TextField(blank=True)
    cancellation_terms = models.TextField(blank=True)
    service_levels = models.TextField(blank=True)
    document = models.FileField(upload_to='suppliers/contracts/', blank=True, null=True)
    status = models.CharField(max_length=24, choices=STATUS, default='draft')
    signed_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_supplier_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-start_date',)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before start date.'})

    def __str__(self):
        return f"{self.contract_number} · {self.supplier}"


class SupplierRate(models.Model):
    contract = models.ForeignKey(SupplierContract, on_delete=models.CASCADE, related_name='rates')
    service = models.ForeignKey(SupplierService, on_delete=models.SET_NULL, blank=True, null=True, related_name='contract_rates')
    description = models.CharField(max_length=200)
    unit = models.CharField(max_length=40)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    valid_from = models.DateField()
    valid_to = models.DateField()
    cancellation_deadline_hours = models.PositiveIntegerField(default=24)

    def clean(self):
        if self.valid_to < self.valid_from:
            raise ValidationError({'valid_to': 'Valid-to date cannot be before valid-from date.'})

    def __str__(self):
        return f"{self.description} · {self.amount} {self.currency}"


class ServiceRequirement(models.Model):
    STATUS = [
        ('required', 'Required'), ('sourcing', 'Sourcing'), ('quoted', 'Quoted'),
        ('selected', 'Selected'), ('contracted', 'Contracted'), ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'), ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='service_requirements')
    category = models.ForeignKey(SupplierCategory, on_delete=models.PROTECT, related_name='requirements')
    title = models.CharField(max_length=200)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=40, default='service')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=200)
    budget_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    needed_by = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='required')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_service_requirements')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('start_at',)

    def clean(self):
        errors = {}
        if self.end_at <= self.start_at:
            errors['end_at'] = 'End time must be after start time.'
        if self.needed_by >= self.start_at:
            errors['needed_by'] = 'Needed-by date must be before service starts.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.title} · {self.tour}"


class RequestForQuote(models.Model):
    STATUS = [
        ('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed'),
        ('awarded', 'Awarded'), ('cancelled', 'Cancelled'),
    ]
    requirement = models.OneToOneField(ServiceRequirement, on_delete=models.CASCADE, related_name='rfq')
    reference = models.CharField(max_length=80, unique=True)
    instructions = models.TextField(blank=True)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_rfqs')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_open(self):
        return self.status == 'published' and self.deadline > timezone.now()

    def __str__(self):
        return self.reference


class SupplierQuote(models.Model):
    STATUS = [
        ('submitted', 'Submitted'), ('under_review', 'Under review'),
        ('selected', 'Selected'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn'),
    ]
    rfq = models.ForeignKey(RequestForQuote, on_delete=models.CASCADE, related_name='quotes')
    supplier = models.ForeignKey(ServiceSupplier, on_delete=models.CASCADE, related_name='quotes')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    details = models.TextField()
    cancellation_terms = models.TextField(blank=True)
    valid_until = models.DateTimeField()
    attachment = models.FileField(upload_to='suppliers/quotes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('amount', 'submitted_at')
        constraints = [models.UniqueConstraint(fields=('rfq', 'supplier'), name='unique_supplier_rfq_quote')]

    def __str__(self):
        return f"{self.rfq} · {self.supplier}"


class ServiceOrder(models.Model):
    STATUS = [
        ('draft', 'Draft'), ('issued', 'Issued'), ('confirmed', 'Confirmed'),
        ('in_service', 'In service'), ('delivered', 'Delivered'), ('completed', 'Completed'),
        ('disputed', 'Disputed'), ('cancelled', 'Cancelled'),
    ]
    order_number = models.CharField(max_length=80, unique=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='service_orders')
    requirement = models.OneToOneField(ServiceRequirement, on_delete=models.SET_NULL, blank=True, null=True, related_name='service_order')
    supplier = models.ForeignKey(ServiceSupplier, on_delete=models.PROTECT, related_name='service_orders')
    contract = models.ForeignKey(SupplierContract, on_delete=models.SET_NULL, blank=True, null=True, related_name='service_orders')
    quote = models.OneToOneField(SupplierQuote, on_delete=models.SET_NULL, blank=True, null=True, related_name='service_order')
    service = models.ForeignKey(SupplierService, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')
    description = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=40, default='service')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    confirmation_reference = models.CharField(max_length=120, blank=True)
    voucher = models.FileField(upload_to='suppliers/vouchers/', blank=True, null=True)
    cancellation_terms = models.TextField(blank=True)
    operational_note = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_service_orders')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_service_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('start_at',)

    def clean(self):
        if self.end_at <= self.start_at:
            raise ValidationError({'end_at': 'End time must be after start time.'})

    def __str__(self):
        return f"{self.order_number} · {self.supplier}"


class SupplierInvoice(models.Model):
    STATUS = [
        ('submitted', 'Submitted'), ('under_review', 'Under review'), ('approved', 'Approved'),
        ('scheduled', 'Scheduled'), ('paid', 'Paid'), ('rejected', 'Rejected'), ('disputed', 'Disputed'),
    ]
    service_order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    issued_at = models.DateField()
    due_date = models.DateField()
    attachment = models.FileField(upload_to='suppliers/invoices/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='submitted')
    payment_reference = models.CharField(max_length=160, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-issued_at',)
        constraints = [models.UniqueConstraint(fields=('service_order', 'invoice_number'), name='unique_order_invoice_number')]

    def clean(self):
        if self.due_date < self.issued_at:
            raise ValidationError({'due_date': 'Due date cannot be before invoice date.'})

    def __str__(self):
        return f"{self.invoice_number} · {self.service_order}"


class SupplierReview(models.Model):
    service_order = models.OneToOneField(ServiceOrder, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_reviews_given')
    quality = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    timeliness = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    contract_compliance = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    invoice_accuracy = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    overall = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.overall}/5 · {self.service_order.supplier}"
