from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



app_name = 'seller'

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('registration/', views.registration, name='registration'),
    path('registrationdone/', views.regdone, name='registerdone'),
    path('portal/', views.portal, name='portal'),

    path('addproducts/', views.addproducts, name='addproducts'),
    path('get-models/', views.get_models_by_brand, name='get_models'),

    path('listedproducts/', views.listedproducts, name='listedproducts'),
    path('toggle-product-status/<int:product_id>/', views.toggle_product_status, name='toggle_product_status'),

    path('update-product/<int:product_id>/', views.update_product, name='update_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),

    path("create-booking/", views.create_booking, name="create_booking"),


    path('orders/', views.seller_orders, name='orders'),
    path('update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),
    
    path('analytics/', views.analytics, name='analytics'),
    path('support/', views.support, name='support'),
    path('mystore/', views.mystore, name='mystore'),
    path('payments/', views.payments, name='payments'),

    path('logout/', views.seller_logout, name='logout'),
    path('accountsettings/', views.accountsettings, name='accountsettings'),
     
] 

