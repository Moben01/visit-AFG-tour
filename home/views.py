from django.shortcuts import render
from django.utils.translation import get_language

# Create your views here.

def home_view(request):
    language_code = get_language()

    if language_code == 'fa' or language_code == "ar":
            # Do something for right-to-left languages
        return render(request, 'RTL/index.html')
    else:
        return render(request, 'index.html')

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)