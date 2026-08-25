from django.contrib import admin
from .models import Country,User,Brand,Category

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Country,CountryAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','id_country')
admin.site.register(User,UserAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display = ('id','name_brand')
admin.site.register(Brand,BrandAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name')
admin.site.register(Category,CategoryAdmin)
# Register your models here.
