from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('home/', views.home, name='home'),
    path('account/',views.account_view, name='account'),
    path('my-product/',views.myProduct_view, name='my-product'),
    path('add-product/', views.addAjax, name='addProduct'),
    path('edit-product/<int:product_id>/',views.editProduct,name='editProduct'),
    path('detail-product/<int:product_id>/',views.detailProduct,name='detailProduct')

]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)