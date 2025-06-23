from django.shortcuts import render

# Create your views here.

def kabul(request):
    return render(request, 'states/kabul.html')

def parwan(request):
    return render(request, 'states/parwan.html')

def maidan_wardak(request):
    return render(request, 'states/maidan_wardak.html')

def Kandahar(request):
    return render(request, 'states/Kandahar.html')