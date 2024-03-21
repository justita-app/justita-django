import code
from django.shortcuts import render
from multiprocessing import context
from django.shortcuts import render , redirect  
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ippanel import Client, Error, HTTPError, ResponseCode
from django.contrib.auth import get_user_model


User = get_user_model()





def home(request):
    if request.user.is_authenticated:
        if request.user.is_lawyer:            
            return redirect('lawyers:lawyers')
         

    return render(request,'base/home.html')


def online_attorney(request)    :
    return render(request , 'base/online-atterney.html')
    
    
def immigrations(request):
    
    return render(request , 'base/immigrations.html')


def about(request):
    return render(request , 'base/about.html')


def aboutEng(request):
    return render(request , 'base/about_english.html')


def immigration(request):
    form = immigrationForm()
  
    if request.method == 'POST':       
        form = immigrationForm(request.POST)
        if form.is_valid():
          form.save()         
          return (redirect('base:done'))


def ccl(request):
    return render(request , 'base/ccl.html')

def tos(request):
    return render(request , 'base/tos.html')
    
def download(request):
    return render(request, 'base/download-justita.html')
def lawyers_tos(request):
    return render(request, 'base/lawyers-tos.html')