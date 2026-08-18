from django.contrib import admin
from .models import Blog

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title','author','created_at')
# Register your models here.
    search_fields = (
        'title',
        'description',
    )

    list_filter = (
        'created_at',
        'author',
    )
admin.site.register(Blog,BlogAdmin)