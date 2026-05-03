# views.py in the main app
from django.shortcuts import render
from seller.models import addProduct
from django.db.models import Q
from django.http import JsonResponse

def home(request):
   # Base query for active products
    products = addProduct.objects.filter(isActive=True)

   

    # Pass products to the template
    context = {
        'products': products,
    }
    return render(request, 'index.html', context)

