from django.shortcuts import render

# Create your views here.

def kabul(request):
    return render(request, 'states/kabul.html')