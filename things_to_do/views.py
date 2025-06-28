from django.shortcuts import render

# Create your views here.
import requests
from django.shortcuts import render

def Art_and_Culture(request):

    return render(request, 'things_to_do/Art_and_Culture.html')


