from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from .models import UserDetails

def index(request):
    if request.method =="POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        UserDetails.objects.create(
            email=email,
            password=password
        )

        return redirect("index") #Reload page after saving to database
    
    return render(request, "main/index.html")