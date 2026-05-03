from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from seller.models import ShopRegistration, ShopDetail, addProduct, productImage, BookingOrder
from .models import Sale
from django.core.mail import send_mail
from django.conf import  settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
import json
from customAdmin.models import Brand, Model
from datetime import datetime, timedelta
from datetime import datetime
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io, os
from decimal import Decimal
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import logging
logger = logging.getLogger(__name__)
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.exceptions import ValidationError







# Frontpage view (no login required)
def frontpage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.isSeller: 
                try:
                    shop = ShopRegistration.objects.get(user=user, isActive=True)
                    if shop:
                        login(request, user)
                        return redirect('seller:portal')
                except ShopRegistration.DoesNotExist:
                    messages.error(request, 'Your shop is not active.')
            else:
                messages.error(request, 'You do not have seller permissions.')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'front.html')

# Registration view
@login_required
def registration(request):
    if request.method == 'POST':
        shopname = request.POST.get('shopname')
        city = request.POST.get('city')
        area = request.POST.get('area')
        location = request.POST.get('location')
        
        if shopname and city and area and location:
            shop_registration = ShopRegistration(
                user=request.user,
                shopname=shopname,
                city=city,
                area=area,
                location=location
            )
            shop_registration.save()
            return redirect(reverse('seller:registerdone'))
        else:
            return render(request, 'registration.html', {'error': 'All fields are required.'})

    return render(request, 'registration.html')


# registration done
def regdone(request):
     return render(request,'registerdone.html')


#portal
@login_required(login_url='/seller/')
def portal(request):
    try:
        shop = ShopRegistration.objects.get(user=request.user, isActive=True)
    except ShopRegistration.DoesNotExist:
        shop = None

    return render(request, 'portalbase.html', {'shop': shop})

@login_required(login_url='/seller/')
def addproducts(request):
    if request.method == "POST":
        shop = request.user.shops.first()
        if not shop:
            messages.error(request, "No shop associated with the user.")
            return redirect('seller:addproducts')

        # Extract and validate form data
        brand_id = request.POST.get("brand")
        model_id = request.POST.get("model")
        imei = request.POST.get("imei")
        condition = request.POST.get("condition")
        colors = request.POST.get("custom_color")
        color2 = request.POST.get("custom_color2")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        seller_sku = request.POST.get("seller_sku")
        exchange = request.POST.get("exchange") == "yes"

        # Validate required fields
        if not (brand_id and model_id and imei and condition and colors and description and price and stock and seller_sku):
            messages.error(request, "All fields are required except the optional color2.")
            return redirect('seller:addproducts')

        # Validate IMEI number
        if len(imei) != 15 or not imei.isdigit():
            messages.error(request, "IMEI number should be 15 digits.")
            return redirect('seller:addproducts')

        try:
            price = Decimal(price)
            stock = int(stock)
        except (ValueError, TypeError):
            messages.error(request, "Invalid price or stock value.")
            return redirect('seller:addproducts')

        # Retrieve brand and model
        try:
            brand = Brand.objects.get(id=brand_id)
            model = Model.objects.get(id=model_id)
        except (Brand.DoesNotExist, Model.DoesNotExist):
            messages.error(request, "Invalid brand or model selected.")
            return redirect('seller:addproducts')

        # Save the product
        product = addProduct.objects.create(
            fk_ShopID=shop,
            brand1=brand.name,
            model=model.name,
            imei=imei,
            condition=condition,
            colors=colors,
            color2=color2,
            description=description,
            price=price,
            stock=stock,
            seller_sku=seller_sku,
            exchange=exchange,
        )

        # Handle product images
        images = request.FILES.getlist('images')
        ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']

        for image in images:
            if image.name.split('.')[-1].lower() not in ALLOWED_EXTENSIONS:
                messages.error(request, "Only JPG, JPEG, and PNG images are allowed.")
                return redirect('seller:addproducts')
            productImage.objects.create(fk_addProduct=product, image=image)

        messages.success(request, "Product added successfully.")
        return redirect('seller:addproducts')

    # Fetch brands for the dropdown
    brands = Brand.objects.all()
    return render(request, 'addproducts.html', {'brands': brands})



#get models by brand

def get_models_by_brand(request):
    """Fetch models based on the selected brand."""
    brand_id = request.GET.get('brand_id')  # Get brand_id from the request
    if brand_id:
        models = Model.objects.filter(brand_id=brand_id).values('id', 'name')  # Fetch models related to the brand
        return JsonResponse({'models': list(models)})  # Convert queryset to a list and return as JSON
    return JsonResponse({'models': []})  # Return an empty list if brand_id is not provided

@login_required(login_url='/seller/')
def listedproducts(request):
    # Get the shops owned by the logged-in user
    user_shops = request.user.shops.all()

    # Fetch all products for the user's shops
    products = addProduct.objects.filter(fk_ShopID__in=user_shops).select_related('fk_ShopID').prefetch_related('images')

    # Render the template with the products
    return render(request, 'listedproducts.html', {'products': products})

# to change the status of a product
@login_required(login_url='/seller/')
def toggle_product_status(request, product_id):
    if request.method == "POST":
        try:
            # Get the product belonging to the user's shop
            product = addProduct.objects.get(productID=product_id, fk_ShopID__user=request.user)
            # Toggle the isActive status
            product.isActive = not product.isActive
            product.save()
            return JsonResponse({'success': True, 'isActive': product.isActive})
        except addProduct.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found.'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

@login_required(login_url='/seller/')
@csrf_exempt
def update_product(request, product_id):
    if request.method == "POST":
        try:
            product = addProduct.objects.get(productID=product_id, fk_ShopID__user=request.user)
            data = json.loads(request.body)
            product.price = data.get('price', product.price)
            product.stock = data.get('stock', product.stock)
            product.save()
            return JsonResponse({'success': True})
        except addProduct.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

@login_required(login_url='/seller/')
@csrf_exempt
def delete_product(request, product_id):
    if request.method == "POST":
        try:
            product = addProduct.objects.get(productID=product_id, fk_ShopID__user=request.user)
            product.delete()
            return JsonResponse({'success': True})
        except addProduct.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


@login_required
@require_http_methods(["POST"])
def create_booking(request):
    try:
        with transaction.atomic():
            # Log all POST data
            logger.debug(f"POST data received: {request.POST}")
            
            # Extract data
            product_id = request.POST.get("product_id")
            quantity = request.POST.get("quantity")
            user_phone = request.POST.get("phone")
            
            # Log extracted data
            logger.debug(f"Extracted data - Product ID: {product_id}, Quantity: {quantity}, Phone: {user_phone}")

            # Validate all required fields are present
            missing_fields = []
            if not product_id:
                missing_fields.append("product_id")
            if not quantity:
                missing_fields.append("quantity")
            if not user_phone:
                missing_fields.append("phone")

            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                logger.error(error_msg)
                return JsonResponse({
                    "success": False,
                    "error": error_msg,
                    "missing_fields": missing_fields
                }, status=400)

            # Convert quantity to integer
            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                return JsonResponse({
                    "success": False,
                    "error": "Invalid quantity value"
                }, status=400)

            # Get product and validate stock
            product = get_object_or_404(addProduct, productID=product_id)
            
            if product.stock < quantity:
                return JsonResponse({
                    "success": False,
                    "error": f"Only {product.stock} items available in stock"
                }, status=400)

            # Create booking
            booking = BookingOrder.objects.create(
                user=request.user,
                product=product,
                shop=product.fk_ShopID,
                quantity=quantity,
                user_phone=user_phone,
                status='Pending'
            )

            # Update product stock
            product.stock -= quantity
            product.save()

            return JsonResponse({
                "success": True,
                "message": "Booking created successfully",
                "booking_id": booking.id
            })

    except Exception as e:
        logger.exception("Error in create_booking view")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
    

@login_required
def seller_orders(request):
    # Get the logged-in user's shops
    seller_shops = ShopRegistration.objects.filter(user=request.user)
    
    # Get all orders for the seller's shops with related data
    orders = BookingOrder.objects.filter(
        shop__in=seller_shops
    ).select_related(
        'user',
        'product',
        'shop'
    ).prefetch_related(
        'product__images'
    ).order_by('-booking_date')

    context = {
        'orders': orders,
    }
    return render(request, 'orderManagement.html', context)


@login_required
def update_order_status(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order = get_object_or_404(BookingOrder, id=order_id)
            action = data.get('action')
            
            if action == 'confirm':
                order.status = 'Confirmed'
                order.save()
                return JsonResponse({'message': 'Booking confirmed successfully.'})
            
            elif action == 'cancel':
                order.status = 'Cancelled'
                order.sold = False
                order.save()
                return JsonResponse({'message': 'Booking cancelled successfully.'})
            
            elif action == 'sold':
                cnic = data.get('cnic')
                imei = data.get('imei')
                
                if not cnic or not imei:
                    return JsonResponse({'error': 'CNIC and IMEI are required'}, status=400)
                
                order.status = 'Confirmed'
                order.sold = True
                order.cnic = cnic
                order.imei = imei
                order.save()
                return JsonResponse({'message': 'Order marked as sold successfully.'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)




@login_required(login_url='/seller/')
def analytics(request):
    sales = Sale.objects.all().order_by('date')
    dates = [sale.date.strftime('%d %b') for sale in sales]
    amounts = [sale.amount for sale in sales]
    
    return render(request, "analytics.html", {'dates': dates, 'amounts': amounts})




@login_required(login_url='/seller/')
def support(request):
    try:
        # Get the users active shop registration
        shop = ShopRegistration.objects.get(user=request.user, isActive=True)
    except ShopRegistration.DoesNotExist:
        shop = None

    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message = request.POST.get('detail', '')
        user_email = request.user.email  # Get sender's email

        if shop:
            # Create the email message
            full_subject = f"{shop.shopname}: {subject}"
            
            # Format the message with additional details
            formatted_message = f"""
Support Ticket Details:
----------------------
From: {user_email}
Shop ID: {shop.shopID}
Shop Name: {shop.shopname}

Message:
{message}
            """
            
            try:
                # Create EmailMessage instance
                email = EmailMessage(
                    subject=full_subject,
                    body=formatted_message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=['rajafajad0921@gmail.com'],
                    reply_to=[user_email]  # Set reply-to as user's email
                )
                
                # Send the email
                email.send(fail_silently=False)
                messages.success(request, "Your message has been sent successfully.")
                
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
        else:
            messages.error(request, "Your shop is not active. Please contact support.")

    # Prepare default values for the form fields
    default_shop_id = shop.shopID if shop else ''
    default_shop_name = shop.shopname if shop else ''
    default_email = request.user.email

    return render(request, 'support.html', {
        'default_shop_id': default_shop_id,
        'default_shop_name': default_shop_name,
        'default_email': default_email,
    })

@login_required(login_url='/seller/')
def mystore(request):
    try:
        shop = ShopRegistration.objects.get(user=request.user, isActive=True)
        shop_detail, created = ShopDetail.objects.get_or_create(fk_ShopID=shop)
    except ShopRegistration.DoesNotExist:
        shop = None
        shop_detail = None

    if request.method == 'POST':
        # Parse opening and closing times
        default_date = timezone.now().date()
        opening_time_str = request.POST.get('shop_open', '')
        closing_time_str = request.POST.get('shop_close', '')
        policy = request.POST.get('policy', '')

        try:
            shop_detail.shop_open = datetime.strptime(f"{default_date} {opening_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            shop_detail.shop_open = None

        try:
            shop_detail.shop_close = datetime.strptime(f"{default_date} {closing_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            shop_detail.shop_close = None

        shop_detail.holiday_mode = request.POST.get('holiday_mode') == 'on'

        shop_detail.policy = policy

        # Handle image upload
        if 'shop_image' in request.FILES:
            image = request.FILES['shop_image']

            # Delete the old image
            if shop_detail.image:
                if os.path.isfile(shop_detail.image.path):
                    os.remove(shop_detail.image.path)

            # Open and resize the image
            img = Image.open(image)
            img = img.convert("RGB")
            img.thumbnail((250, 100), Image.Resampling.LANCZOS)

            # Crop to fit the exact size
            if img.width > 250 or img.height > 100:
                left = (img.width - 250) / 2
                top = (img.height - 100) / 2
                right = (img.width + 250) / 2
                bottom = (img.height + 100) / 2
                img = img.crop((left, top, right, bottom))

            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            img_io.seek(0)
            img_name = f"{shop.shopname}_logo.jpg"
            shop_detail.image = InMemoryUploadedFile(
                img_io, None, img_name, 'image/jpeg', img_io.tell(), None
            )

        # Save the updated details
        shop_detail.save()
        messages.success(request, "Store details updated successfully.")

    return render(request, 'store.html', {
        'shop': shop,
        'shop_detail': shop_detail,
    })
   


@login_required(login_url='/seller/')
def payments(request):
     return render(request, 'payments.html')

@login_required(login_url='/seller/')
def accountsettings(request):
     return render(request, 'accountSettings.html')

def seller_logout(request):
     logout(request)
     return redirect('seller:frontpage')


