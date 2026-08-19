from django.urls import path
from . import views

urlpatterns = [
    path('',views.blog_list,name='blog_list'),
    path('rate/', views.blog_rate, name='blog_rate'),
    path('comment/',views.blog_comment,name='blog_comment'),
    path('<int:blog_id>/',views.blog_detail,name='blog_detail'),
]