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

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'Category'

    def __str__(self):
        return self.name

class Brand(models.Model):
    name_brand = models.CharField(max_length=100)

    class Meta:
        db_table = 'Brand'

    def __str__(self):
        return self.name_brand

class Product(models.Model):
    user = models.ForeignKey(
        User,on_delete=models.CASCADE,related_name='products'
    )

    name = models.CharField(max_length=255)

    images = models.TextField(null=True,blank=True)

    price = models.DecimalField(max_digits=12,decimal_places=2)

    sale_status = models.IntegerField(default=0)

    sale = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL,null=True,blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True,blank=True)

    detail = models.TextField(blank=True,
    null=True)

    def __str__(self):
        return self.name


# Create your models here.
