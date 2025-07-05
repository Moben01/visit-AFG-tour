from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model

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


class Translator(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        
    ]

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    languages = models.CharField(max_length=200, help_text="e.g. English ↔ Pashto, Chinese ↔ Dari")
    nationality = models.CharField(max_length=50, blank=True)
    experience_years = models.PositiveIntegerField()
    certifications = models.TextField(blank=True, help_text="Translation certificates or qualifications")
    bio = models.TextField(blank=True)
    available_from = models.DateField(null=True, blank=True)
    available_to = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='translators/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

