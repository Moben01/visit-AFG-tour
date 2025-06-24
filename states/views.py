from django.shortcuts import render

# Create your views here.

def kabul(request):
    return render(request, 'states/kabul.html')


def balkh(request):
    return render(request, 'states/balkh.html')


def samangan(request):
    return render(request, 'states/samangan.html')


def jawzjan(request):
    return render(request, 'states/jawzjan.html')


def faryab(request):
    return render(request, 'states/faryab.html')


def SarePol(request):
    return render(request, 'states/SarePol.html')


def Baghlan(request):
    return render(request, 'states/Baghlan.html')


def Kunduz(request):
    return render(request, 'states/Kunduz.html')


def Takhar(request):
    return render(request, 'states/Takhar.html')


def Badakhshan(request):
    return render(request, 'states/Badakhshan.html')