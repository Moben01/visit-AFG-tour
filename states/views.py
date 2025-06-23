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





# states for west


def Herat(request):
    return render(request, 'states/Herat.html')



def Farah(request):
    return render(request, 'states/Farah.html')

def Badghis(request):
    return render(request, 'states/Badghis.html')

def Ghor(request):
    return render(request, 'states/Ghor.html')


