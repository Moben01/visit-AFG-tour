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



class Tour(models.Model):
    category = models.ForeignKey(TourCategory, on_delete=models.CASCADE, related_name='tours')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to = 'tour-image/')
    slug = models.SlugField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=100)
    duration_days = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    google_location = models.CharField(max_length=2000000)
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
    tour = models.ForeignKey('Tour', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booked_tours')
    booking_date = models.DateField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    paid = models.BooleanField(default=False)
    paid_amount = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)


    def __str__(self):
        return f"{self.user} booked {self.tour} on {self.booking_date.strftime('%Y-%m-%d')}"


class ItineraryItem(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary_items')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    date = models.DateTimeField()
    image = models.ImageField(upload_to = 'itenary-images')

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






from django.db import models



from django.db import models

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




class Languages(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=100)
    total_price = models.FloatField()

    def __str__(self):
        return f"language {self.name} | code {self.code}"


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


# AccommodationBooking

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
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.FloatField(default=0)
    image = models.ImageField(upload_to='accommodation_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='accommodation_gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.accommodation.name}"

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
        return f"{self.get_type_display()} from {self.departure_location} to {self.arrival_location}"

class TransportImage(models.Model):
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='transport_gallery/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.transport}"

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