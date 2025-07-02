from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import TranslatorForm
from tour.models import TourCategory






def translator_view(request):
    message = ""  # پیام خالی در ابتدا
    form = TranslatorForm()

    if request.method == 'POST':
        form = TranslatorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            message = "The information has been successfully registered."

    context = {
        'form': form,
        'message': message,
        'get_tour_categories': TourCategory.objects.all() 
    }
    return render(request, 'tour_involve/translator.html', context)
