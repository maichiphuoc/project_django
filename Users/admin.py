from django.contrib import admin
from .models import Country,User

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Country,CountryAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','id_country')
admin.site.register(User,UserAdmin)
# Register your models here.
