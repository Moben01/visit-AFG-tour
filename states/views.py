from django.shortcuts import render

# Create your views here.

def kabul(request):
    return render(request, 'states/kabul.html')

def parwan(request):
    return render(request, 'states/parwan.html')

def maidan_wardak(request):
    return render(request, 'states/maidan_wardak.html')












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
