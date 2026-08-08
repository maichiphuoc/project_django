from django.db import models
from django.conf import settings


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    # password = models.CharField(max_length=50
    # )
    # first_name = models.CharField(max_length=10)
    # last_name = models.CharField(max_length=10)
    # avatar = models.ImageField(upload_to='users_image',null=True)
    id_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null= True,blank=True)

    def __str__(self):
        return self.username
# Create your models here.
