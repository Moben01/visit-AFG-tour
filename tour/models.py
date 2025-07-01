from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

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


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/')


class Booking(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    persons = models.PositiveIntegerField()
    booking_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.tour.title}"


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

class Includes(models.Model):
        tour =models.ForeignKey(Tour, on_delete=models.CASCADE)
        title =models.CharField(max_length=500)

    
class Excludes(models.Model):
        tour =models.ForeignKey(Tour, on_delete=models.CASCADE)
        title =models.CharField(max_length=500)
