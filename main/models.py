from django.db import models

# Create your models here.
class UserDetails(models.Model):
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "user_details"

    def __str__(self):
        return self.email
    
class SensorDetails(models.Model):
    date_time = models.DateTimeField(primary_key=True)

    battery_charge = models.FloatField(null=True, blank=True)
    battery_voltage = models.FloatField(default=0.0)
    battery_output = models.FloatField(default=0.0)
    battery_temperature = models.FloatField(null=True, blank=True)

    solar_output = models.FloatField(null=True, blank=True)
    electricityload_value = models.FloatField(null=True, blank=True)
    water_usage = models.FloatField(null=True, blank=True)
    gas_usage = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "sensor_details"
        ordering = ["-date_time"]

    def __str__(self):
        return str(self.date_time)


class WeatherPulled(models.Model):
    day = models.DateField(primary_key=True)

    status = models.CharField(max_length=100, null=True, blank=True)
    min_temp = models.FloatField(null=True, blank=True)
    max_temp = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "weather_pulled"
        ordering = ["day"]

    def __str__(self):
        return str(self.day)
    
class Misc(models.Model):
    text_id = models.TextField(primary_key=True)
    filter_value = models.IntegerField(default=0)
    sort_value = models.IntegerField(default=0)
    filter_type = models.TextField(null=True, blank=True)
    filter_range = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "misc"

    def __str__(self):
        return self.text_id