from django.shortcuts import render, redirect
from django.http import JsonResponse
#from django.http import HttpResponseRedirect
#from django.urls import reverse #used to dynamically generate a URL path based on a URL pattern's assigned name
from django.views.decorators.cache import never_cache #Decorator that adds headers to a response so that it will never be cached
from .models import UserDetails
from django.utils.html import mark_safe
from .models import SensorDetails
from .models import Misc
from .models import WeatherPulled
from django.conf import settings

import re
import json
import datetime

#--------------Auth cookie endpoint stuff
def set_auth_cookie(response, user_email):
    response.set_signed_cookie(
        'auth_token',
        user_email,
        salt=settings.SIGNED_COOKIE_SALT,
        max_age=86400 * 7, #7 Days converted into seconds
        httponly=True, #Not accessible via javascript
        samesite='Lax',
        path='/'
    )

def delete_auth_cookie(response): #Delet cookie on response
    response.delete_cookie('auth_token', path='/')

#Get user email from the cookie
def get_authenticated_user(request):
    try:
        email = request.get_signed_cookie(
            'auth_token',
            salt=settings.SIGNED_COOKIE_SALT
        )
        return UserDetails.objects.get(email=email)
    except (KeyError, UserDetails.DoesNotExist): #Handle errors 'gracefully'
        return None

#Redirect to index if auth_token is not present or invalid
def auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = get_authenticated_user(request)
        if user is None:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

#Return index.html on site load.
def index(request):
    return render(request, "main/index.html")

#Take signup details, return errors, add to database
def signup(request):
    if request.method =="POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")
        security_question = request.POST.get("security_question")
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
        if security_question == "":
            return render(request, "main/index.html", {"error":"You must answer the security question!"})

        UserDetails.objects.create(
            email=email,
            password=password,
            name=name,
            security_question=security_question
        )

        return redirect("signup") #Reload page after saving to database
    
    return render(request, "main/index.html")

#Manage login, if valid, redirect to dashboard
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
                response = redirect("dashboard")
                set_auth_cookie(response, user_details.email) #Set cookie.
                return response #Redirect user to dashboard after validating their account details are correct

        except:
            raise RuntimeError("Email does not exist")

        #if db_email == email:

        return redirect("") #Reload page after failed login
    
    return render(request, "main/index.html")

#Manage logout, delete cookie
def logout(request):
    if request.method =="POST":
        response = redirect("/")
        delete_auth_cookie(response)
        return response
    return redirect("/")

#Take range's start value for RawDataDisplay's filter, update database with those values, call doDashboardLogic() and return dashboard.html
def setRanStart(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        Misc.objects.filter(text_id=1).update(ran_Start=str(data.get("rdd_StartRan")))
        response = render(request, "main/dashboard.html", doDashboardLogic())
        #Force clear browser caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
#Take range's end value for RawDataDisplay's filter, update database with those values, call doDashboardLogic() and return dashboard.html
def setRanEnd(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        Misc.objects.filter(text_id=1).update(ran_End=str(data.get("rdd_EndRan")))
        response = render(request, "main/dashboard.html", doDashboardLogic())
        #Force clear browser caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

#Take filtered value for RawDataDisplay's filter, update database with that string, call doDashboardLogic() and return dashboard.html
def setFilter(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        Misc.objects.filter(text_id=1).update(filter_type=str(data.get("rdd_FilterType")))
        response = render(request, "main/dashboard.html", doDashboardLogic())
        #Force clear browser caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

#Get user's RawDataDisplay chosen filter type (None, Value or Range) in number form
@never_cache #auto injects headers that tell the browser nothing is stored cache
def filter(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        #Used for test logging
        #with open("output.txt", "w", encoding="utf-8") as f:
        #    f.write(str(data.get("number")))
        Misc.objects.filter(text_id=1).update(filter_value=str(data.get("number")))
        return redirect("dashboard")

#Get user's RawDataDisplay chosen sort type (Latest, Oldest, Value Ascending, Value Descending or Alphabetical) in number form
@never_cache #auto injects headers that tell the browser nothing is stored cache
def sort(request):
    if request.method =="POST":
        data = json.loads(request.body.decode("utf-8"))
        Misc.objects.filter(text_id=1).update(sort_value=str(data.get("number")))
        return redirect("sort")
    if request.method =="GET":
        return redirect("dashboard")

#Perform filtering on selected list, with the specified type (None, Range, Type).
#Using filters depending on the chosen type, (e.g.filter for water_usage only, or filter all values between start_range and end_range).
def rdd_filter(list, f_type, filter='None', ranStart=0, ranEnd=100):
    if f_type == str("None"):
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(str(list))
        filtered_list = list
        return filtered_list
    if f_type == str("Range"):
        filtered_list = [x for x in list if (float(ranStart) <= float(x["value"]) <= float(ranEnd))]
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(str(filtered_list))
        return filtered_list
    if f_type == str("Type"):
        filtered_list = [x for x in list if x["type"] == filter]
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(str(filtered_list))
        return filtered_list


def dictKey(key, element):
    return element[key]

def dictKeyDT(key, element):
    return datetime.datetime.strptime(element[key], "%H:%M")

#Perform sorting on the selected list, with the specified type of sorting (Latest, Oldest, Value Ascending, Value Descending or Alphabetical)
def rdd_sort(list, sort_type):
    match sort_type:
        case "Latest":
            return sorted(list, key=lambda x: dictKeyDT("date_time", x))
        case "Oldest":
            return sorted(list, key=lambda x: dictKeyDT("date_time", x), reverse=True)
        case "Value Ascending":
            return sorted(list, key=lambda x: dictKey("value", x))
        case "Value Descending":
            return sorted(list, key=lambda x: dictKey("value", x), reverse=True)
        case "Alphabetical":
            return sorted(list, key=lambda x: dictKey("type", x))

class GraphHandler: #Class to handle graph generation and retention
    def __init__(self):
        self.__elecLoadValues = []
        self.__waterValues = []
        self.__gasValues = []
        self.__batteryValues = []
        self.__solarValues = []
        self.__times = []

    def update_array(self):
        #Here we take the last 5 entries in the SensorDetails table within the database
        Sensor_last5 = SensorDetails.objects.order_by("-date_time")[:5]

        #Create empty lists for each column within the table
        self.__elecLoadValues = []
        self.__waterValues = []
        self.__gasValues = []
        self.__batteryValues = []
        self.__solarValues = []
        self.__times = []
        #Append each entry's values into a list
        for i in Sensor_last5:
            self.__elecLoadValues.append(i.electricityload_value) #Add each entry's electricityload_value to the list
            self.__waterValues.append(i.water_usage) #Add each entry's water_usage to the list
            self.__gasValues.append(i.gas_usage) #Add each entry's gas_usage to the list
            self.__batteryValues.append(i.battery_charge) #Add each entry's battery_charge to the list
            self.__solarValues.append(i.solar_output) #Add each entry's solar_output to the list
            self.__times.append(f"{str(i.date_time.strftime("%H:%M"))}") #Add the time of each entry to the list
        
    def get_graph(self, type): #Match for the graph type, return the makeGraph function or makeMixedGraph utilising private class variables
        match type:
            case "batt_vs_solar":
                return makeMixedGraph("battVsSolar_graph", "Battery Charge VS Solar Output", "Time", "Output (W)", "Battery Output (W)", "Solar Output (W)", self.__times, self.__batteryValues, self.__solarValues)
            case "electricity_load":
                return makeGraph("electricityload_graph", "Electricity Load", "Time", "Load (W)", self.__times, self.__elecLoadValues)
            case "water_usage":
                return makeGraph("waterUsage_graph", "Water Usage", "Time", "Water Used (L)", self.__times, self.__waterValues)
            case "gas_usage":
                return makeGraph("gasUsage_graph", "Gas Usage", "Time", "Gas Used (L)", self.__times, self.__gasValues)



#Take all data from the database relevant to the dashboard, interpret it, and return context for a HTTP response.
#The data provided within the context is fed into the dashboard's html, css and javascript code dynamically.
def doDashboardLogic():
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
    sel_filter_type = str("None")

    #First we check for the type of filter that must be applied (None, Range or Type).
    #Then we return the newly filtered list (can be the unmanipulated list, if the filter type is none)
    #Then we take the filtered* list, and sort it depending on the type of sorting algorithm chosen by the user.
    #Finally we return the manipulated list (allows for the following combinations: an unsorted but filtered list, OR a filtered AND sorted list)
    match filter_n:
        case 0: 
            sel_filter_type = str("None")
            filtered_list = rdd_filter(AllData, sel_filter_type)
        case 1:
            sel_filter_type = str("Range")
            filtered_list = rdd_filter(AllData, sel_filter_type, rdd_type, rdd_StartRan, rdd_EndRan)
        case 2:
            sel_filter_type = str("Type")
            filtered_list = rdd_filter(AllData, sel_filter_type, rdd_type)
    match sort_n:
        case 0:
            sort_type = 'Latest'
            sorted_list = rdd_sort(filtered_list, sort_type)
        case 1:
            sort_type = 'Oldest'
            sorted_list = rdd_sort(filtered_list, sort_type)
        case 2:
            sort_type = 'Value Ascending'
            sorted_list = rdd_sort(filtered_list, sort_type)
        case 3:
            sort_type = 'Value Descending'
            sorted_list = rdd_sort(filtered_list, sort_type)
        case 4:
            sort_type = 'Alphabetical'
            sorted_list = rdd_sort(filtered_list, sort_type)
    
    graph_handler = GraphHandler()
    graph_handler.update_array()
    
    #I then render the graphs by passing it through to the frontend under defined variables
    #mark_safe used to treat the string as trusted HTML (stops auto-escaping by Django)
    context = {
    "battVsSolar_graph_api": mark_safe(graph_handler.get_graph("batt_vs_solar")),
    "electricityload_graph_api": mark_safe(graph_handler.get_graph("electricity_load")),
    "waterUsage_graph_api": mark_safe(graph_handler.get_graph("water_usage")),
    "gasUsage_graph_api": mark_safe(graph_handler.get_graph("gas_usage")),
    "graphHeight": graphHeight,
    "graphWidth": graphWidth,
    "rawDataDisplay_filter": sel_filter_type,
    "rawDataDisplay_sort": sort_type,
    "rawDataDisplay_filter_n": filter_n,
    "rawDataDisplay_sort_n": sort_n,
    "rawDataDisplay_value_list": sorted_list
    }
    
    return context

def doRDDLogic(request):
    misc = Misc.objects.get(text_id=1)
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

    sel_filter_type = "None"
    sort_type = "Latest"
    match misc.filter_value:
        case 0: 
            sel_filter_type = str("None")
            filtered_list = rdd_filter(AllData, "None")
        case 1:
            sel_filter_type = str("Range")
            filtered_list = rdd_filter(AllData, "Range", misc.filter_type, misc.ran_Start, misc.ran_End)
        case 2:
            sel_filter_type = str("Type")
            filtered_list = rdd_filter(AllData, "Type", misc.filter_type)
    match misc.sort_value:
        case 0:
            sort_type = 'Latest'
            sorted_list = rdd_sort(filtered_list, 'Latest')
        case 1:
            sort_type = 'Oldest'
            sorted_list = rdd_sort(filtered_list, 'Oldest')
        case 2:
            sort_type = 'Value Ascending'
            sorted_list = rdd_sort(filtered_list, 'Value Ascending')
        case 3:
            sort_type = 'Value Descending'
            sorted_list = rdd_sort(filtered_list, 'Value Descending')
        case 4:
            sort_type = 'Alphabetical'
            sorted_list = rdd_sort(filtered_list, 'Alphabetical')
    return JsonResponse({"data": sorted_list, "filter_type": sel_filter_type, "sort_type": sort_type})

def doBreakdownLogic(request):
    weekly_weather = WeatherPulled.objects.order_by("day")[:7] #Pull last 7 entries
    data = []
    for w in weekly_weather:
        data.append({ #Return the max and min temp for each day, along with the status
            "day": w.day,
            "max_temp": w.max_temp,
            "min_temp": w.min_temp,
            "status": w.status
        })
    return JsonResponse({"data": data})

def batteryStats(request):
    latest = SensorDetails.objects.order_by("-date_time").first()
    data = {
        "battery_output": latest.battery_output,
        "battery_voltage": latest.battery_voltage,
        "battery_charge": latest.battery_charge,
        "battery_temperature": latest.battery_temperature
    }
    return JsonResponse(data)

def insightLogic(request):
    all_sensors = SensorDetails.objects.order_by("-date_time") #Sort db by date_time (latest).
    latest = all_sensors[0]
    n = len(all_sensors)
    total_elec = 0.0 #Create empty vars
    total_water = 0.0
    total_gas = 0.0
    total_battery = 0.0
    total_solar = 0.0
    total_batt_temp = 0.0

    insight = ""

    max_elec = float("-inf")
    max_water = float("-inf")
    max_gas = float("-inf")
    min_battery = float("-inf")

    for s in all_sensors:
        #Accumulate all averages
        if s.electricityload_value is not None: #existence checks
            total_elec += s.electricityload_value
        if s.water_usage is not None:
            total_water += s.water_usage
        if s.gas_usage is not None:
            total_gas += s.gas_usage
        if s.battery_charge is not None:
            total_battery += s.battery_charge
        if s.solar_output is not None:
            total_solar += s.solar_output
        if s.battery_temperature is not None:
            total_batt_temp += s.battery_temperature

        #Calculate max and min values
        if s.electricityload_value is not None and s.electricityload_value > max_elec:
            max_elec = s.electricityload_value
        if s.water_usage is not None and s.water_usage > max_water:
            max_water = s.water_usage
        if s.gas_usage is not None and s.gas_usage > max_gas:
            max_gas = s.gas_usage
        if s.battery_charge is not None and s.battery_charge < min_battery:
            min_battery = s.battery_charge

    #Calculate averages
    avg_elec = round(total_elec / n, 1)
    avg_water = round(total_water / n, 1)
    avg_gas = round(total_gas / n, 1)
    avg_battery = round(total_battery / n, 1)
    avg_solar = round(total_solar / n, 1)
    avg_batt_temp = round(total_batt_temp / n, 1)

    #Handle cases where values are None
    if max_elec == float("-inf"):
        max_elec = 0
    if max_water == float("-inf"):
        max_water = 0
    if max_gas == float("-inf"):
        max_gas = 0
    if min_battery == float("inf"):
        min_battery = 0

    #Insight conditions
    #1)High electricity load
    if avg_elec > 0 and latest.electricityload_value and latest.electricityload_value > (avg_elec * 1.5):
        insight += (
            "Your current electricity load ({}W) is significantly above average ({}W). "
            "Considering unplugging non-essential devices or scheduling high power-drawing appliances "
            "to run during off-peak hours, reducing the strain on your system!"
        ).format(latest.electricityload_value, avg_elec)

    #2)Water usage spike
    elif avg_water > 0 and latest.water_usage and latest.water_usage > (avg_water * 2.0):
        insight += (
            "Your water usage has spiked to {}L, which is double your {}L average! "
            "Consider checking for dripping faucets and irrigation leaks."
        ).format(latest.water_usage, avg_water)
    
    #3)Gas usage spike
    elif avg_gas > 0 and latest.gas_usage and latest.gas_usage > (avg_gas * 1.5):
        insight += (
            "Your gas usage is unusally high {}L, compared to your {}L average. "
            "If it's cold, try putting on some extra layers before turning up the heat."
        ).format(latest.gas_usage, avg_gas)

    #4)Battery critically low
    elif latest.battery_charge is not None and latest.battery_charge < 20:
        insight += (
            "Your battery charge is critically low at {}%. You should considering "
            "reducing non-essential appliance usage and letting your solar panels recharge "
            "before running any heavy loads."
        ).format(latest.battery_charge)

    #5)Solar output high
    elif (latest.battery_temperature is not None and latest.battery_charge is not None
          and latest.solar_output > (latest.battery_charge * 1.2)
          and latest.solar_output > 100):
        insight += (
            "Your solar panels are outputting {}W! That's a lot! "
            "Consider doing a load of washing now, and running other high-load appliances!"
        ).format(latest.solar_output)
    
    #6)Battery temperature too high
    elif (latest.battery_temperature is not None and latest.battery_temperature > 40):
        insight += (
            "Your battery temperature is {}°C, which is above the ideal 20-30°C range. "
            "Heat reduces battery lifespan!"
        ).format(latest.battery_temperature)

    #7)Solar output dipping and battery low
    elif (latest.solar_output is not None and latest.battery_charge is not None
          and latest.solar_output < 50 and latest.battery_charge < 50):
        insight += (
            "Solar output is dropping ({}W) and battery is at {}%. "
            "Start conserving energy for the evening, to avoid draining the battery over night."
        ).format(latest.solar_output, latest.battery_charge)

    #8)Efficiency tip: Battery below average despite good solar
    elif (avg_battery > 0 and latest.battery_charge is not None and latest.solar_output is not None
          and latest.battery_charge < avg_battery and latest.solar_output > 200):
        insight += (
            "Your battery ({}%) is below average ({}%) despite good solar ({}W). "
            "Consider checking if your charge controller is working correctly."
        ).format(latest.battery_charge, avg_battery, latest.solar_output)

    #9)Normal - no proper insights
    else:
        insight += (
            "All sensors appear to be outputting normal data! "
            "Keep up the utility efficient habits!"
        )

    return JsonResponse({"insight": insight})

#Return dashboard.html on page visit (with context from doDashboardLogic()).
@never_cache #auto injects headers that tell the browser nothing is stored cache
@auth_required #Cookie required, otherwise blocked.
def dashboard(request):
    if request.method =="GET":
        response = render(request, "main/dashboard.html", doDashboardLogic())
        #Force clear browser caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    return render(request, "main/dashboard.html")

#Create and return a line graph with a given title, x-axis and y-axis labels, and specified values for the x and y-axis.
#Here we pass JSON as plain text after variables are embedded into it!
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

#Create and return a 'mixed' line graph (graph with two y-axis datasets for a single x-axis dataset) with a given title,
#x-axis and y-axis labels, and specified values for the x and y-axis.
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