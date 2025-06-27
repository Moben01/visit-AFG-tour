from django.shortcuts import render

# Create your views here.

def visa_guide(request):
    return render(request, 'plan_your_trip/visa_guide.html')