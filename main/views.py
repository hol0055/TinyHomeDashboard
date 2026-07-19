from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse #used to dynamically generate a URL path based on a URL pattern's assigned name
from django.views.decorators.cache import never_cache #Decorator that adds headers to a response so that it will never be cached
from .models import UserDetails
from django.utils.html import mark_safe
from .models import SensorDetails
from .models import Misc

import re
import json

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

def setRan(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        Misc.objects.filter(text_id=1).update(ran_Start=str(data.get("rdd_StartRan")))
        Misc.objects.filter(text_id=1).update(ran_End=str(data.get("rdd_EndRan")))
        return redirect("dashboard")

def setFilter(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        Misc.objects.filter(text_id=1).update(filter_type=str(data.get("rdd_FilterType")))
        return redirect("dashboard")


def logout(request): #Need to implement cookie to store logged in state, & block access to dash if not present
    if request.method =="POST":
        return redirect("")
    return render(request, "main/dashboard.html")
@never_cache #auto injects headers that tell the browser nothing is stored cache
def filter(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        #Used for test logging
        #with open("output.txt", "w", encoding="utf-8") as f:
        #    f.write(str(data.get("number")))
        Misc.objects.filter(text_id=1).update(filter_value=str(data.get("number")))
        #Misc.objects.filter(text_id=1).update(ran_End=str(data.get("rdd_EndRan")))
        #Misc.objects.filter(text_id=1).update(ran_Start=str(data.get("rdd_StartRan")))
        #response = HttpResponseRedirect(reverse("dashboard"))
        #response['Refresh'] = '0'
        #return response
        return redirect("dashboard")
        
@never_cache #auto injects headers that tell the browser nothing is stored cache
def sort(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        Misc.objects.filter(text_id=1).update(sort_value=str(data.get("number")))
        #return render(request, "main/dashboard.html", {"rawDataDisplay_sort": str(data.get("number"))})
        return redirect("sort")
    if request.method =="GET":
        return redirect("dashboard")

def rdd_filter(list, f_type, filter='None', ranStart=0, ranEnd=3):
    if f_type == 'None':
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(str(list))
        return list
    if f_type == 'Range':
        for i in list:
            filtered_list = [x for x in list if (float(ranStart) < float(x["value"]) < float(ranEnd))]
            #for i in filtered_list:
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(str(filtered_list))
        return filtered_list
    if f_type == 'Type':
        for i in list:
            filtered_list = [x for x in list if x["type"] == f"{filter}"]
            #for i in filtered_list:
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(str(filtered_list))
        return filtered_list

def rdd_sort(list, sort_type):
    pass

def SetRan(request):
    pass

@never_cache #auto injects headers that tell the browser nothing is stored cache
def dashboard(request):
    if request.method =="GET":
        #graphHeight = "250px"
        #graphWidth = "350px"
        #customGraphs = ''
        #if customGraphs != 0:
        graphHeight = "200px"
        graphWidth = "300px"

        Sensor_all = SensorDetails.objects.order_by("-date_time") #Get all entries in the SensorDetails table
        AllData = []
        
        for r in Sensor_all:
            dt = f"{str(r.date_time.strftime('%H:%M'))}"
            AllData.extend([
                {"type": "battery_charge", "date_time": dt, "value": r.battery_charge},
                {"type": "battery_voltage", "date_time": dt, "value": r.battery_voltage},
                {"type": "battery_output", "date_time": dt, "value": r.battery_output},
                {"type": "battery_temperature", "date_time": dt, "value": r.battery_temperature},
                {"type": "solar_output", "date_time": dt, "value": r.solar_output},
                {"type": "electricityload_value", "date_time": dt, "value": r.electricityload_value},
                {"type": "water_usage", "date_time": dt, "value": r.water_usage},
                {"type": "gas_usage", "date_time": dt, "value": r.gas_usage},
            ])

            

        filter_n = Misc.objects.get(text_id=1).filter_value #Get filter and sort value from pk=1 in misc table
        sort_n = Misc.objects.get(text_id=1).sort_value
        rdd_type = Misc.objects.get(text_id=1).filter_type
        rdd_StartRan = Misc.objects.get(text_id=1).ran_Start
        rdd_EndRan = Misc.objects.get(text_id=1).ran_End

        match filter_n:
            case 0: 
                sel_filter_type = 'None'
                filtered_list = rdd_filter(AllData, sel_filter_type)
            case 1:
                sel_filter_type = 'Range'
                filtered_list = rdd_filter(AllData, sel_filter_type, rdd_StartRan, rdd_EndRan)
            case 2:
                sel_filter_type = 'Type'
                filtered_list = rdd_filter(AllData, sel_filter_type, rdd_type)
        match sort_n:
            case 0:
                sort_type = 'Latest'
                rdd_sort(AllData, sort_type)
            case 1:
                sort_type = 'Oldest'
                rdd_sort(AllData, sort_type)
            case 2:
                sort_type = 'Value Ascending'
                rdd_sort(AllData, sort_type)
            case 2:
                sort_type = 'Value Descending'
                rdd_sort(AllData, sort_type)
            case 3:
                sort_type = 'Alphabetical'
                rdd_sort(AllData, sort_type)
        

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
        electricityload_graph_api_string = makeGraph("electricityload_graph", "Electricity Load", "Time", "Load (W)", times, elecLoadValues)
        waterUsage_graph_api_string = makeGraph("waterUsage_graph", "Water Usage", "Time", "Water Used (L)", times, waterValues)
        gasUsage_graph_api_string = makeGraph("gasUsage_graph", "Gas Usage", "Time", "Gas Used (L)", times, gasValues)
        #I then render the graph by passing it through to the frontend under the variable electricityload_graph_api, allowing me to directly render the code onto the page!
        if sel_filter_type == "Range":
            response = render(request, "main/dashboard.html", {
            "battVsSolar_graph_api": mark_safe(battVsSolar_graph_api_string),
            "electricityload_graph_api": mark_safe(electricityload_graph_api_string),
            "waterUsage_graph_api": mark_safe(waterUsage_graph_api_string),
            "gasUsage_graph_api": mark_safe(gasUsage_graph_api_string),
            "graphHeight": graphHeight,
            "graphWidth": graphWidth,
            "rawDataDisplay_filter": sel_filter_type,
            "rawDataDisplay_sort": sort_type,
            "rawDataDisplay_filter_n": filter_n,
            "rawDataDisplay_sort_n": sort_n,
            "rawDataDisplay_value_list": filtered_list,
            "rawDataDisplay_filter_isRan":"True"
            }) #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)
        elif sel_filter_type == 'Type':
            response = render(request, "main/dashboard.html", {
            "battVsSolar_graph_api": mark_safe(battVsSolar_graph_api_string),
            "electricityload_graph_api": mark_safe(electricityload_graph_api_string),
            "waterUsage_graph_api": mark_safe(waterUsage_graph_api_string),
            "gasUsage_graph_api": mark_safe(gasUsage_graph_api_string),
            "graphHeight": graphHeight,
            "graphWidth": graphWidth,
            "rawDataDisplay_filter": sel_filter_type,
            "rawDataDisplay_sort": sort_type,
            "rawDataDisplay_filter_n": filter_n,
            "rawDataDisplay_sort_n": sort_n,
            "rawDataDisplay_value_list": filtered_list,
            "rawDataDisplay_filter_isType":"True"
            }) #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)
        else:
            response = render(request, "main/dashboard.html", {
            "battVsSolar_graph_api": mark_safe(battVsSolar_graph_api_string),
            "electricityload_graph_api": mark_safe(electricityload_graph_api_string),
            "waterUsage_graph_api": mark_safe(waterUsage_graph_api_string),
            "gasUsage_graph_api": mark_safe(gasUsage_graph_api_string),
            "graphHeight": graphHeight,
            "graphWidth": graphWidth,
            "rawDataDisplay_filter": sel_filter_type,
            "rawDataDisplay_sort": sort_type,
            "rawDataDisplay_filter_n": filter_n,
            "rawDataDisplay_sort_n": sort_n,
            "rawDataDisplay_value_list": filtered_list
            }) #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)
    
        #Force clear browser caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
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
                size: 16,
                weight: 'bold',
                family: 'Helvetica'
            }},
            padding: {{
                top: 10,
                bottom: 10
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
                size: 16,
                weight: 'bold',
                family: 'Helvetica'
            }},
            padding: {{
                top: 10,
                bottom: 10
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