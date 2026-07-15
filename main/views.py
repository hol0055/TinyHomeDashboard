from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from .models import UserDetails

import re

def index(request):
    return render(request, "main/index.html")

def signup(request):
    if request.method =="POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")
        regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
        try:
            if re.fullmatch(regex, email) == None:
                return render(request, "main/index.html", {"error":"You entered an invalid email address."})
        except:
            return render(request, "main/index.html", {"error":"You entered an invalid email address."})
        if password == "":
            return render(request, "main/index.html", {"error":"You must enter a password."})
        if name == "":
            return render(request, "main/index.html", {"error":"You must enter a name."})

        UserDetails.objects.create(
            email=email,
            password=password,
            name=name
        )

        return redirect("signup") #Reload page after saving to database
    
    return render(request, "main/index.html")

def login(request):
    if request.method =="POST":
        emailGiven = request.POST.get("email")
        password = request.POST.get("password")
        regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
        try:
            if re.fullmatch(regex, emailGiven) == None:
                return render(request, "main/index.html", {"error":"You entered an invalid email address."})
        except:
            return render(request, "main/index.html", {"error":"You entered an invalid email address."})
        if password == "":
            return render(request, "main/index.html", {"error":"You must enter a password."})
        
        try:
            user = UserDetails.objects.all() #get(email=emailGiven)
            user_details = user.get(email=emailGiven)
            if user_details.password == password:
            #return render(request, "main/index.html", {"error":user_details})
                return redirect("dashboard") #Redirect user to dashboard after validating their account details are correct

        except:
            raise RuntimeError("Email does not exist")

        #if db_email == email:


        return redirect("login") #Reload page after failed login
    
    return render(request, "main/index.html")

def dashboard(request):
    #if request.method =="POST":
        #
    return render(request, "main/dashboard.html")