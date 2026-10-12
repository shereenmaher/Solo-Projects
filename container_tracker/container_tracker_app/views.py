from django.shortcuts import render , HttpResponse,redirect
from .models import *
from .import models

def index(request):
    return render(request,"reg_log.html")

def dashboard(request):
    return render(request,"dashboard.html")
