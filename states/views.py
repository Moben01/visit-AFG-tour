from django.shortcuts import render
from tour.models import *
from things_to_do.models import *
from django.http import HttpResponse
# Create your views here.

def kabul(request):
    get_tour_categories = TourCategory.objects.all()
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Kabul")
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Kabul")

    return render(request, 'states/kabul.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def kabul_maping(request):
    get_tour_categories = TourCategory.objects.all()    
    return render(request, 'states/kabul-map.html', {'get_tour_categories':get_tour_categories})


def balkh(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Balkh")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Balkh")

    return render(request, 'states/balkh.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})



def samangan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Samangan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Samangan")

    return render(request, 'states/samangan.html', 
    {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})


def jawzjan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Jowzjan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Jowzjan")

    return render(request, 'states/jawzjan.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})


def faryab(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Faryab")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Faryab")

    return render(request, 'states/faryab.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})


def SarePol(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Sar-e Pol")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Sar-e Pol")

    return render(request, 'states/SarePol.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})


def Baghlan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Baghlan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Baghlan")

    return render(request, 'states/Baghlan.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})


def Kunduz(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Kunduz")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Kunduz")

    return render(request, 'states/Kunduz.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})


def Takhar(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Takhar")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Takhar")

    return render(request, 'states/Takhar.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})


def Badakhshan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Badakhshan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Badakhshan")

    return render(request, 'states/Badakhshan.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def parwan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Parwan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Parwan")

    return render(request, 'states/parwan.html', {'get_tour_categories':get_tour_categories,'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})










def maidan_wardak(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Wardak")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Wardak")
    return render(request, 'states/maidan_wardak.html', {'get_tour_categories':get_tour_categories,'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})





def bamyan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Bamyan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Bamyan")
    return render(request, 'states/bamyan.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def logar(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Logar")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Logar")

    return render(request, 'states/logar.html', {'get_tour_categories':get_tour_categories,'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})







def kapisa(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Kapisa")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Kapisa")

    return render(request, 'states/kapisa.html', {'get_tour_categories':get_tour_categories,'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def panjshir(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Panjshir")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Panjshir")

    return render(request, 'states/panjshir.html', {'get_tour_categories':get_tour_categories,'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})





def daikundi(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Daykundi")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Daykundi")

    return render(request, 'states/daikundi.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def ghazni(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Ghazni")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Ghazni")
    return render(request, 'states/ghazni.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def paktika(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Paktia")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Paktia")
    return render(request, 'states/paktika.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def khost(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Khost")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Khost")
    return render(request, 'states/khost.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})











# all the East  province 


def Nangarhar(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Nangarhar")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Nangarhar")
    return render(request, 'states/Nangarhar.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})





def Kunar(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Kunar")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Kunar")
    return render(request, 'states/Kunar.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})





def Laghman(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Laghman")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Laghman")
    return render(request, 'states/Laghman.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})





def Nuristan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Nuristan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Nuristan")
    return render(request, 'states/Nuristan.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})



  # South Provinces 
def Kandahar(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Kandahar")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Kandahar")
    return render(request, 'states/Kandahar.html', {'get_tour_categories':get_tour_categories, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province,'find_best_places_in_this_province':find_best_places_in_this_province})

def Helmand(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Helmand")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Helmand")
    return render(request, 'states/Helmand.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def Zabul(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Zabul")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Zabul")
    return render(request, 'states/Zabul.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def Uruzgan(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Urozgan")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Urozgan")
    return render(request, 'states/Uruzgan.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def Nimroz(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Nimroz")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Nimroz")
    return render(request, 'states/Nimroz.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def Paktika(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Paktika")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Paktika")
    return render(request, 'states/Paktieka.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})




# states for west


def Herat(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Herat")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Herat")
    return render(request, 'states/Herat.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})



def Farah(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Farah")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Farah")
    return render(request, 'states/Farah.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def Badghis(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Badghis")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Badghis")

    return render(request, 'states/Badghis.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})

def Ghor(request):
    get_tour_categories = TourCategory.objects.all()
    find_things_to_do_in_this_province = Top_things_to_do_in_province.objects.filter(provinces__icontains = "Ghor")
    find_best_places_in_this_province = Best_places_for_visit.objects.filter(provinces__icontains = "Ghor")
    return render(request, 'states/Ghor.html', {'get_tour_categories':get_tour_categories, 'find_best_places_in_this_province':find_best_places_in_this_province, 'find_things_to_do_in_this_province':find_things_to_do_in_this_province})