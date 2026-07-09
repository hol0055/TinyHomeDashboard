from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import UserDetails


def index(request):
    return render(request, "main/index.html")