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