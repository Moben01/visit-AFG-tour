from django.shortcuts import render

# Create your views here.

def visa_guide(request):
    return render(request, 'plan_your_trip/visa_guide.html')

def essentials(request):
    return render(request, 'plan_your_trip/essentials.html')

def flight(request):
    return render(request, 'plan_your_trip/flight.html')

def Accommodation(request):
    return render(request, 'plan_your_trip/Accommodation.html')

def Getting_to_around_afg(request):
    return render(request, 'plan_your_trip/Getting_to_around_afg.html')