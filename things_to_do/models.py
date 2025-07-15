from django.db import models
from multiselectfield import MultiSelectField

class Best_places_for_visit(models.Model):
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

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='place_images/')
    description = models.TextField()  # 📌 added for details
    location = models.CharField(max_length=200)
    provinces = MultiSelectField(choices=PROVINCE_CHOICES, max_choices=34, max_length=400)

    def __str__(self):
        return self.title


class Best_places_for_visit_images(models.Model):
    place = models.ForeignKey(Best_places_for_visit, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='place_images/more/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image of {self.place.title}"