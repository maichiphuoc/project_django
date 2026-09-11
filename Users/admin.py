from django.contrib import admin
from .models import Country,User,Brand,Category,Cart,CartItem

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

class CartAdmin(admin.ModelAdmin):
    list_display = ('id','user')
admin.site.register(Cart,CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
admin.site.register(CartItem,CartItemAdmin)
# Register your models here.


