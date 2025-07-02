from django.shortcuts import render
from tour.models import *
# Create your views here.

def kabul(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/kabul.html', {'get_tour_categories':get_tour_categories})

def kabul_maping(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/kabul-map.html', {'get_tour_categories':get_tour_categories})


def balkh(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/balkh.html', {'get_tour_categories':get_tour_categories})


def samangan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/samangan.html', {'get_tour_categories':get_tour_categories})


def jawzjan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/jawzjan.html', {'get_tour_categories':get_tour_categories})


def faryab(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/faryab.html', {'get_tour_categories':get_tour_categories})


def SarePol(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/SarePol.html', {'get_tour_categories':get_tour_categories})


def Baghlan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Baghlan.html', {'get_tour_categories':get_tour_categories})


def Kunduz(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Kunduz.html', {'get_tour_categories':get_tour_categories})


def Takhar(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Takhar.html', {'get_tour_categories':get_tour_categories})


def Badakhshan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Badakhshan.html', {'get_tour_categories':get_tour_categories})

def parwan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/parwan.html', {'get_tour_categories':get_tour_categories})

def maidan_wardak(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/maidan_wardak.html', {'get_tour_categories':get_tour_categories})

def bamyan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/bamyan.html', {'get_tour_categories':get_tour_categories})

def logar(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/logar.html', {'get_tour_categories':get_tour_categories})

def kapisa(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/kapisa.html', {'get_tour_categories':get_tour_categories})

def panjshir(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/panjshir.html', {'get_tour_categories':get_tour_categories})

def daikundi(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/daikundi.html', {'get_tour_categories':get_tour_categories})

def ghazni(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/ghazni.html', {'get_tour_categories':get_tour_categories})

def paktika(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/paktika.html', {'get_tour_categories':get_tour_categories})

def khost(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/khost.html', {'get_tour_categories':get_tour_categories})











# all the East  province 


def Nangarhar(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Nangarhar.html', {'get_tour_categories':get_tour_categories})





def Kunar(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Kunar.html', {'get_tour_categories':get_tour_categories})





def Laghman(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Laghman.html', {'get_tour_categories':get_tour_categories})





def Nuristan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Nuristan.html', {'get_tour_categories':get_tour_categories})



  # South Provinces 
def Kandahar(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Kandahar.html', {'get_tour_categories':get_tour_categories})

def Helmand(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Helmand.html', {'get_tour_categories':get_tour_categories})

def Zabul(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Zabul.html', {'get_tour_categories':get_tour_categories})

def Uruzgan(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Uruzgan.html', {'get_tour_categories':get_tour_categories})

def Nimroz(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Nimroz.html', {'get_tour_categories':get_tour_categories})

# def Ghazni(request):    get_tour_categories = TourCategory.objects.all()

#     return render(request, 'states/Ghaznie.html', {'get_tour_categories':get_tour_categories})

def Paktika(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Paktieka.html', {'get_tour_categories':get_tour_categories})




# states for west


def Herat(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Herat.html', {'get_tour_categories':get_tour_categories})



def Farah(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Farah.html', {'get_tour_categories':get_tour_categories})

def Badghis(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Badghis.html', {'get_tour_categories':get_tour_categories})

def Ghor(request):
    get_tour_categories = TourCategory.objects.all()

    return render(request, 'states/Ghor.html', {'get_tour_categories':get_tour_categories})


