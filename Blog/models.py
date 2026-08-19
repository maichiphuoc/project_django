from django.db import models
from django.conf import settings
from django.contrib import admin

from django.utils import timezone
from django.contrib.auth.models import User

class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    # image = models.ImageField(upload_to='blog_images',null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    class Meta:
        db_table = 'Blog'

class Rate(models.Model):
    rate = models.IntegerField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

class Comments(models.Model):
    comment = models.TextField()
    author_name = models.TextField()
    author_image = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='replies')
    level = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
# Create your models here.
