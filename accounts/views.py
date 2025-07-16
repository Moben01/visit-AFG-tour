from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

# views.py
@login_required
def account_settings(request):
    return render(request, 'account/settings.html')
