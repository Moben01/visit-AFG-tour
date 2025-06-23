from django.shortcuts import render

# Create your views here.

def kabul(request):
    return render(request, 'states/kabul.html')

def parwan(request):
    return render(request, 'states/parwan.html')

def maidan_wardak(request):
    return render(request, 'states/maidan_wardak.html')

def bamyan(request):
    return render(request, 'states/bamyan.html')

def logar(request):
    return render(request, 'states/logar.html')

def kapisa(request):
    return render(request, 'states/kapisa.html')

def panjshir(request):
    return render(request, 'states/panjshir.html')

def daikundi(request):
    return render(request, 'states/daikundi.html')

def ghazni(request):
    return render(request, 'states/ghazni.html')

def paktika(request):
    return render(request, 'states/paktika.html')

def khost(request):
    return render(request, 'states/khost.html')