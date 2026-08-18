from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser



class Country(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'Country'

    def __str__(self):
        return self.name

class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='image_avatars',
        null=True,
        blank=True
    )

    id_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'User'

    def __str__(self):
        return self.username
# Create your models here.
