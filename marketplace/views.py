from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import CustomUser
from seller.models import addProduct, ShopRegistration, ShopDetail, BookingOrder
from customAdmin.models import Brand, Model, Specification
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.

    
# Main Marketplace Page

def main_marketplace(request, user_id=None):
    # Get the user
    if user_id:
        user = get_object_or_404(CustomUser, pk=user_id)
    else:
        user = request.user

    # Capture search query and initialize products queryset
    query = request.GET.get('q', '').strip()  # Capture 'q' parameter from the navbar
    products = addProduct.objects.filter(isActive=True)  # Base queryset

    # Search by product model (case-insensitive)
    if query:
        products = products.filter(model__icontains=query)

    # Capture and apply filters dynamically
    condition = request.GET.get('condition')
    city = request.GET.get('city')
    color = request.GET.get('color')
    exchange = request.GET.get('exchange')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    if condition:
        products = products.filter(condition=condition)
    if city:
        products = products.filter(fk_ShopID__city__iexact=city)
    if color:
        products = products.filter(Q(colors=color) | Q(color2=color))
    if exchange:
        exchange_value = exchange.lower() == 'true'  # Convert 'true'/'false' string to boolean
        products = products.filter(exchange=exchange_value)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # Debug print to verify request parameters and queryset
    print(f"Query: {query}, Filters: {request.GET.dict()}, Products Count: {products.count()}")

    # Context for the template
    context = {
        'products': products,
        'user': user,
    }

    return render(request, 'main_marketplace.html', context)

# Search Suggestions

def search_suggestions(request):
    print("Search Suggestions Request:", request.GET)
    query = request.GET.get('term', '')
    suggestions = []

    if query:
        suggestions = list(
            addProduct.objects.filter(model__icontains=query)
            .values_list('model', flat=True)
            .distinct()
        )

    return JsonResponse(suggestions, safe=False)

def custom_logout(request):
    logout(request)
    return redirect('/')




def product_description_page(request, product_id):
    # Fetch the product details
    product = get_object_or_404(addProduct, productID=product_id)
    product_images = product.images.all()

    # Get latest booking for this user and product
    latest_booking = None
    if request.user.is_authenticated:
        latest_booking = BookingOrder.objects.filter(
            user=request.user,
            product=product,
            status__in=['Pending', 'Confirmed']  # Only get active bookings
        ).order_by('-created_at').first()

    # Set the initial button state based on booking status
    button_state = {
        'disabled': False,
        'class': 'book-now-btn bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition',
        'text': 'Book Now'
    }

    if product.stock == 0:
        button_state.update({
            'disabled': True,
            'class': 'bg-gray-400 text-white font-bold py-3 px-6 rounded-lg shadow-lg',
            'text': 'Out of Stock'
        })
    elif latest_booking:
        if latest_booking.status == 'Pending':
            button_state.update({
                'disabled': True,
                'class': 'bg-yellow-500 text-white font-bold py-3 px-6 rounded-lg shadow-lg',
                'text': 'Pending Confirmation'
            })
        elif latest_booking.status == 'Confirmed':
            button_state.update({
                'disabled': True,
                'class': 'bg-green-500 text-white font-bold py-3 px-6 rounded-lg shadow-lg',
                'text': 'Booking Confirmed'
            })

    # Fetch related products by brand, excluding the current product
    related_models = addProduct.objects.filter(
        brand1=product.brand1, isActive=True
    ).exclude(productID=product_id)[:4]

    # Check if the user already has an active booking order for this product
    existing_booking_order = None
    if request.user.is_authenticated:
        existing_booking_order = BookingOrder.objects.filter(
            user=request.user,
            product=product,
            status='Active'  # Assuming there's a `status` field in BookingOrder
        ).first()

    # Fetch the specifications for the product model
    model_instance = Model.objects.filter(name=product.model).first()  # Adjust field if needed
    specifications = Specification.objects.filter(model=model_instance)

    # Prepare a general description for the product
    product_table_desc = [
        {'label': 'Brand', 'value': product.brand1},
        {'label': 'Model', 'value': product.model},
        {'label': 'Condition', 'value': product.condition},
        {'label': 'Colors', 'value': product.colors},
        {'label': 'Price', 'value': f'Rs. {product.price}'},
        {'label': 'Stock', 'value': product.stock},
        {'label': 'Exchange Available', 'value': 'Yes' if product.exchange else 'No'},
    ]

    # Prepare the context to send to the template
    context = {
        'product': product,
        'product_images': product_images,
        'latest_booking': latest_booking,
        'button_state': button_state,
        'related_models': related_models,
        'productTableDesc': product_table_desc,
        'existing_booking_order': existing_booking_order,  # BookingOrder details if exists
        'specifications': specifications,  # Specifications for the product model
    }
    return render(request, 'productDescriptionPage.html', context)


@csrf_exempt
def get_seller_info(request):
    if request.method == "POST":
        data = json.loads(request.body)
        shop_id = data.get("shop_id")

        print(f"Shop ID: {shop_id}")

        try:
            shop = ShopRegistration.objects.get(shopID=shop_id)
            return JsonResponse({
                "success": True,
                "phone": shop.user.phone,  # Adjust if the phone field name differs
                "address": shop.city,
            })
        except ShopRegistration.DoesNotExist:
            return JsonResponse({"success": False, "message": "Shop not found."})

    return JsonResponse({"success": False, "message": "Invalid request method."})


#signup page
def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'signup.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'signup.html')

        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
        )
        user.set_password(password)  # Hash the password before saving
        user.save()
        
        return redirect('marketplace:signin')
    
    return render(request, 'signup.html')


#signin page
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(username=email, password=password)  # Use 'username' as 'email' here
        if user:
            login(request, user)
            return redirect('marketplace:main_marketplace', user_id=user.id)
        else:
            return render(request, 'signin.html', {"error": "Invalid email or password."})

    return render(request, 'signin.html')


def cart(request):
    return render(request, 'cart.html')

def store_page(request, store_id):
    shop = get_object_or_404(ShopRegistration, pk=store_id)
    products = addProduct.objects.filter(fk_ShopID=shop, isActive=True)
    shopdetail=ShopDetail.objects.get(fk_ShopID=shop)

    context = {
        'shop': shop,
        'products': products,
        'shopdetail': shopdetail,
    }
    return render(request, 'shopkeeperStore.html', context)




def bookingform(request):
    return render(request, 'bookingform.html')

def aboutUs(request):
    return render(request, 'aboutUs.html')

def privacyPolicy(request): 
    return render(request, 'privacyPolicy.html')

