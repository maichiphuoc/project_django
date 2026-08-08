from django.db import models
from django.conf import settings
from django.contrib import admin

from django.utils import timezone
from django.contrib.auth.models import User

class blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    # image = models.ImageField(upload_to='blog_images',null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    
# Create your models here.
