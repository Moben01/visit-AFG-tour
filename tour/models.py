import re
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from multiselectfield import MultiSelectField
from django.core.validators import MaxValueValidator, MinValueValidator
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
    image = models.ImageField(upload_to = 'tour-image/')
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=120, choices=SCHEDULE_OR_NOT)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()
    location = MultiSelectField(choices=PROVINCE_CHOICES, max_choices=34, max_length=400)
    duration_day = models.CharField(max_length=150)
    duration_night = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    google_location = models.CharField(max_length=2000000)
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, null=True, blank=True)
    security_gard = models.ForeignKey(SecurityGuard, on_delete=models.SET_NULL, null=True, blank=True)
    translator = models.ForeignKey(Translator, on_delete=models.SET_NULL, null=True, blank=True)
    entry_ticket = models.ForeignKey(EntryTicket, on_delete=models.SET_NULL, null=True, blank=True, related_name="entry_tickets")
    permit = models.ForeignKey(Permit, on_delete=models.SET_NULL, null=True, blank=True, related_name="permits")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

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
    ]
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary_items')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    date = models.DateTimeField()
    image = models.ImageField(upload_to = 'itenary-images')
    accommodation = models.ForeignKey(Accommodation, on_delete=models.SET_NULL, blank=True, null=True)
    type_of_transport = models.CharField(max_length=120 ,choices=TRANSPORT_TYPE)
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, blank=True, null=True)
    tour_guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, blank=True, null=True)
    meals = models.ForeignKey(Meal, on_delete=models.SET_NULL, blank=True, null=True)
    logistics = models.ForeignKey(Logistic, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number} - {self.title or 'Itinerary'}"

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