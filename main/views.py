from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from .models import UserDetails
from django.utils.html import mark_safe
from .models import SensorDetails

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


        return redirect("") #Reload page after failed login
    
    return render(request, "main/index.html")

def logout(request): #Need to implement cookie to store logged in state, & block access to dash if not present
    if request.method =="POST":
        return redirect("")
    return render(request, "main/dashboard.html")

def dashboard(request): #BIG WIP -- NEED GRAPHS ACTUALLY WORKING!!
    #if request.method =="POST":
    #   items = [1,2,3]
    #   html = "".join(
    #       f''
    #       for i in items
    #   ) 
    #   return render(request, "main/dashboard.html", {
    #       "rendered_divs": mark_safe(html)
    #   }) #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)
    
    if request.method =="GET":
        Sensor_last5 = SensorDetails.objects.order_by("-date_time")[:5] #Get last 5 entries in the SensorDetails table
        elecLoadValues = []
        waterValues = []
        gasValues = []
        batteryValues = []
        solarValues = []
        times = []
        for i in Sensor_last5:
            elecLoadValues.append(i.electricityload_value) #Add each entry's electricityload_value to the list
            waterValues.append(i.water_usage) #Add each entry's water_usage to the list
            gasValues.append(i.gas_usage) #Add each entry's gas_usage to the list
            batteryValues.append(i.battery_charge) #Add each entry's battery_charge to the list
            solarValues.append(i.solar_output) #Add each entry's solar_output to the list
            times.append(f"{str(i.date_time.strftime("%H:%M"))}") #Add the time of each entry to the list
        #Have to pass the code like this unfortunately, as im attempting to pass json as text in python...
        #Essentially, this line calls the makeGraph function, defining the graph, its data set, labels, and other qualities
        battVsSolar_graph_api_string = makeMixedGraph("battVsSolar_graph", "Battery Charge VS Solar Output", "Time", "Output (W)", "Battery Output (W)", "Solar Output (W)", times, batteryValues, solarValues)
        electricityload_graph_api_string = makeGraph("electricityload_graph", "Electricity Load", "Time", "Load (W)", elecLoadValues, times)
        waterUsage_graph_api_string = makeGraph("waterUsage_graph", "Water Usage", "Time", "Water Used (L)", waterValues, times)
        gasUsage_graph_api_string = makeGraph("gasUsage_graph", "Gas Usage", "Time", "Gas Used (L)", gasValues, times)
        #I then render the graph by passing it through to the frontend under the variable electricityload_graph_api, allowing me to directly render the code onto the page!
        return render(request, "main/dashboard.html", {
            "battVsSolar_graph_api": mark_safe(battVsSolar_graph_api_string),
            "electricityload_graph_api": mark_safe(electricityload_graph_api_string),
            "waterUsage_graph_api": mark_safe(waterUsage_graph_api_string),
            "gasUsage_graph_api": mark_safe(gasUsage_graph_api_string)
            }) #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)
    return render(request, "main/dashboard.html")

"""
ATTEMPT 1
if request.method =="POST":
        Sensor_last5 = SensorDetails.objects.order_by("-date_time")[:5]
        Sensor = SensorDetails.objects.order_by("-date_time")
        n = 0
        for i in Sensor_last5:
            n =+ 1
            value_string = f'"electricityload_value{n}:" {str(i.electricityload_value)}'
            sent_string = f'{value_string},'.join(sent_string) #Append value_string onto the end of sent_string
        return render(request, "main/dashboard.html", {sent_string}) #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)

ATTEMPT 2
if request.method =="POST":
        Sensor_last5 = SensorDetails.objects.order_by("-date_time")[:5]
        Sensor = SensorDetails.objects.order_by("-date_time")
        n = 0
        sent_string = ""
        for i in Sensor_last5:
            value_string = i.electricityload_value
            sent_string = f'{value_string},'.join(sent_string) #Append value_string onto the end of sent_string
        return render(request, "main/dashboard.html", {"electricityload_values": sent_string}) #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)
"""

def makeGraph(graph, title, labelx, labely, valuesx, valuesy):
    return f'''
const {graph}_ctx = document.getElementById('{graph}');
new Chart({graph}_ctx, {{
    type: 'line',
    data: {{
    labels: {valuesx},
    datasets: [{{
        label: '{labely}',
        data: {valuesy},
        borderWidth: 1
    }}]
}},
options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
        title: {{
            display: true,
            text: '{title}',
            color: '#000000',
            font: {{
                size: 20,
                weight: 'bold',
                family: 'Helvetica'
            }},
            padding: {{
                top: 10,
                bottom: 30
            }}
        }}
    }},
    scales: {{
        x: {{
            title: {{
                display: true,
                text: '{labelx}',
                color: '#000000',
                font: {{
                    size: 14,
                    weight: 'normal'
                }}
            }}
        }},
        y: {{
            beginAtZero: false,
            title: {{
                display: true,
                text: '{labely}',
                color: '#000000',
                font: {{
                    size: 14,
                    weight: 'normal'
                }}
            }}
        }}
    }}
}}
}});
'''
'''{graph}_ctx.style.width = '450';
{graph}_ctx.style.height = '450';'''
def makeMixedGraph(graph, title, labelx, labely, labely1, labely2, valuesx, valuesy1, valuesy2):
    return f'''
const ctx = document.getElementById('{graph}');
new Chart(ctx, {{
    type: 'line',
    data: {{
    labels: {valuesx},
    datasets: [{{
        label: '{labely1}',
        data: {valuesy1},
        borderWidth: 1
    }},
    {{
        label: '{labely2}',
        data: {valuesy2},
        borderWidth: 1
    }}
    ]
}},
options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
        title: {{
            display: true,
            text: '{title}',
            color: '#000000',
            font: {{
                size: 20,
                weight: 'bold',
                family: 'Helvetica'
            }},
            padding: {{
                top: 10,
                bottom: 30
            }}
        }}
    }},
    scales: {{
        x: {{
            title: {{
                display: true,
                text: '{labelx}',
                color: '#000000',
                font: {{
                    size: 14,
                    weight: 'normal'
                }}
            }}
        }},
        y: {{
            beginAtZero: false,
            title: {{
                display: true,
                text: '{labely}',
                color: '#000000',
                font: {{
                    size: 14,
                    weight: 'normal'
                }}
            }}
        }}
    }}
}}
}});
'''