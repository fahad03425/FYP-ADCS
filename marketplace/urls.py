from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'marketplace'  

urlpatterns = [

     path('logout/', views.custom_logout, name='logout'),

    path('marketplace/', views.main_marketplace, name='main_marketplace'),
    path('main_marketplace/<int:user_id>/', views.main_marketplace, name='main_marketplace'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),  # AJAX suggestions
   
    path('product/<int:product_id>/', views.product_description_page, name='product_description_page'),

    path('get-seller-info/', views.get_seller_info, name='get_seller_info'),
   

    path('store/<int:store_id>/', views.store_page, name='store'),

    
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('cart/', views.cart, name='cart'),
    path('bookingform/', views.bookingform, name='bookingform'),

    path('aboutus/', views.aboutUs, name='aboutus'),
    path('privacypolicy/', views.privacyPolicy, name='privacypolicy'),

   
]
