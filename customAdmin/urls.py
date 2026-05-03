from django.urls import path
from . import views



app_name = 'customAdmin'

urlpatterns = [
    path('', views.adminlogin, name='customAdmin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('registeredsellers/', views.registeredSellers, name='registeredSellers'),
    path('registeredsellerdetail/<int:shopID>/', views.registeredsellerdetails, name='registeredsellerdetail'),

  
    path('newsellers/', views.newsellers, name='newsellers'),
    path('newsellerdetail/<int:shopID>/', views.newsellerdetail, name='newsellerdetail'),



    path('addphone/', views.addphone, name='addphone'),


    path('category/', views.category, name='category'),

    path('addbrand/', views.brand, name='brand'),
    

    path('model/', views.model, name='model'),


    
    path('specification/', views.specification, name='specification'),
    path('delete-specification/<int:model_id>/', views.delete_specification, name='delete_specification'),

    path('get-models/', views.get_models_by_brand, name='get_models_by_brand'),

    path('adminsettings/', views.adminsettings, name='adminsettings'),

    
    
]