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











# all the East  province 


def Nangarhar(request):
    return render(request, 'states/Nangarhar.html')





def Kunar(request):
    return render(request, 'states/Kunar.html')





def Laghman(request):
    return render(request, 'states/Laghman.html')





def Nuristan(request):
    return render(request, 'states/Nuristan.html')




def Kandahar(request):
    return render(request, 'states/Kandahar.html')

def Helmand(request):
    return render(request, 'states/Helmand.html')

def Zabul(request):
    return render(request, 'states/Zabul.html')




# states for west


def Herat(request):
    return render(request, 'states/Herat.html')



def Farah(request):
    return render(request, 'states/Farah.html')

def Badghis(request):
    return render(request, 'states/Badghis.html')

def Ghor(request):
    return render(request, 'states/Ghor.html')


