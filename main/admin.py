from django.contrib import admin

# Register your models here.
from .models import UserDetails
from .models import SensorDetails
from .models import Misc
from .models import WeatherPulled

admin.site.register(UserDetails)
admin.site.register(SensorDetails)
admin.site.register(Misc)
admin.site.register(WeatherPulled)