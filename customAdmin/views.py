
from django.shortcuts import render, get_object_or_404, redirect
from seller.models import ShopRegistration
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.contrib import messages
import logging, json
from django.http import JsonResponse
from .forms import CategoryForm
from django.views.decorators.csrf import csrf_exempt
from customAdmin.models import Category, Brand, Model, Specification
import uuid

# Create your views here.

logger = logging.getLogger(__name__)

def adminlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:  # Check if the user is a superuser
                login(request, user)  # Log the user in
                return redirect('customAdmin:dashboard')  # Redirect to the admin dashboard
            else:
                messages.error(request, 'You do not have permission to access this page.')  # Show error for non-superusers
        else:
            messages.error(request, 'Invalid username or password.')  # Show error for invalid credentials
            logger.warning(f'Failed login attempt for username: {username}')  # Log the failed attempt

    return render(request, 'adminlogin.html')


@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('customAdmin:customAdmin')  # Redirect if not a superuser

    return render(request, 'dashboard.html')


def registeredSellers(request):
    if request.method == 'POST':
        # Handle the delete request
        shop_id = request.POST.get('shop_id')
        if shop_id:
            shop = get_object_or_404(ShopRegistration, shopID=shop_id)
            # Deactivate the shop and user
            shop.isActive = False
            shop.user.is_seller = False
            shop.user.save()  # Save the user changes
            shop.save()  # Save the shop changes
            
            # Optionally add a success message or log action
            # messages.success(request, 'Seller deactivated successfully.')
            return redirect('customAdmin:registeredSellers')  # Redirect back to the sellers list

    # Fetch all active sellers
    sellers = ShopRegistration.objects.filter(isActive=True)
    return render(request, 'registeredsellers.html', {'sellers': sellers})
    

def registeredsellerdetails(request, shopID):
    seller = get_object_or_404(ShopRegistration, shopID=shopID)
    user = seller.user
    
    
    # Render the template with seller and user details for a GET request
    return render(request, 'registeredsellerdetails.html', {'seller': seller, 'user': user})
    
  

def newsellers(request):
    sellers = ShopRegistration.objects.filter(isActive=False)  # Modify this filter if needed
    return render(request, 'newsellers.html', {'sellers': sellers})


def newsellerdetail(request, shopID):
    seller = get_object_or_404(ShopRegistration, shopID=shopID)
    user = seller.user
    
    # Check if this is a POST request for approval
    if request.method == 'POST':
        seller.isActive = True  # Set shop as active
        user.isSeller = True    # Set user as a seller
        seller.save()
        user.save()
        return redirect('customAdmin:newsellers')  # Redirect to new sellers page after approval
    
    # Render the template with seller and user details for a GET request
    return render(request, 'newsellerdetail.html', {'seller': seller, 'user': user})


def addphone(request):
    return render(request, 'addphone.html')


# category
@require_http_methods(["GET", "POST", "DELETE"])
def category(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, 'categories.html', {'categories': categories})
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get('name')
            slug = data.get('slug')
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'Category name is required'
                })
            
            category = Category(name=name)
            if slug:
                category.slug = slug
                
            category.save()
            return JsonResponse({
                'success': True,
                'message': 'Category added successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)
            category_id = data.get('id')
            
            if not category_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Category ID is required'
                })
            
            # Try to get the category by category_id (not the default id)
            category = Category.objects.get(category_id=category_id)
            category.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Category deleted successfully'
            })
            
        except Category.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Category not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

# Brand View
def brand(request):
    if request.method == "GET":
        # Render the brand page with existing categories and brands
        categories = Category.objects.all()
        brands = Brand.objects.select_related('category').all()
        return render(request, 'brand.html', {'categories': categories, 'brands': brands})

    elif request.method == "POST":
        # Handle brand creation
        try:
            data = json.loads(request.body)
            category_id = data.get('category')
            brand_name = data.get('name')

            if not category_id or not brand_name:
                return JsonResponse({'success': False, 'message': 'Category and brand name are required.'})

            # Fetch the category
            category = Category.objects.filter(category_id=category_id).first()
            if not category:
                return JsonResponse({'success': False, 'message': 'Invalid category selected.'})

            # Create the brand
            brand = Brand.objects.create(category=category, name=brand_name)
            return JsonResponse({'success': True, 'message': f'Brand "{brand.name}" added successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    elif request.method == "DELETE":
        # Handle brand deletion
        try:
            brand_id = request.GET.get('id')
            if not brand_id:
                return JsonResponse({'success': False, 'message': 'Brand ID is required.'})

            brand = Brand.objects.filter(id=brand_id).first()
            if not brand:
                return JsonResponse({'success': False, 'message': 'Brand not found.'})

            brand_name = brand.name
            brand.delete()
            return JsonResponse({'success': True, 'message': f'Brand "{brand_name}" deleted successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def model(request):
    if request.method == "GET":
        categories = Category.objects.all()
        brands = Brand.objects.all()
        models = Model.objects.all().select_related('category', 'brand')
        return render(request, 'model.html', {
            'categories': categories,
            'brands': brands,
            'models': models,
        })

    elif request.method == "POST":
        data = json.loads(request.body)
        category_id = data.get("category")
        brand_id = data.get("brand")
        name = data.get("name")

        if not category_id or not brand_id or not name:
            return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)
        
        # Check if the model already exists
        if Model.objects.filter( brand_id=brand_id, name=name).exists():
            return JsonResponse({
                    'success': False,
                    'message': 'Model already exists for this category and brand.'
                }, status=400)

        category = get_object_or_404(Category, id=category_id)
        brand = get_object_or_404(Brand, id=brand_id)
        model = Model.objects.create(category=category, brand=brand, name=name)
        return JsonResponse({'success': True, 'message': 'Model added successfully.'})

    elif request.method == "DELETE":
        model_id = request.GET.get('id')
        if not model_id:
            return JsonResponse({'success': False, 'message': 'Model ID is required.'}, status=400)

        model = get_object_or_404(Model, model_id=model_id)
        model.delete()
        return JsonResponse({'success': True, 'message': 'Model deleted successfully.'})
    
def specification(request):
    if request.method == "GET":
        categories = Category.objects.all()
        brands = Brand.objects.select_related('category').all()
        specifications = Specification.objects.select_related('model', 'model__brand', 'model__category').all()

        return render(request, 'specification.html', {
            'categories': categories,
            'brands': brands,
            'specifications': specifications
        })

    elif request.method == "POST":
        try:
            # Extract data from the POST request
            data = request.POST
            model_id = data.get("model")
            ram = data.get("ram")
            storage = data.get("memory")
            battery = data.get("battery")
            sim_type = data.get("sim_type")
            e_sim = data.get("e_sim")

            # Check if a specification already exists for the given model_id
            if Specification.objects.filter(model_id=model_id).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Specification for this model already added."
                })

            # Fetch the Model instance
            model_instance = Model.objects.get(id=model_id)

            # Create the Specification
            Specification.objects.create(
                model=model_instance,
                ram=ram,
                storage=storage,
                battery=battery,
                sim_type=sim_type,
                e_sim=e_sim
            )

            return JsonResponse({"success": True, "message": "Specification added successfully."})

        except Model.DoesNotExist:
            return JsonResponse({"success": False, "message": "Invalid model selected."})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method."})

def delete_specification(request, model_id):
    if request.method == "POST":
        try:
            # Fetch all specifications associated with the given model_id
            specifications = Specification.objects.filter(model__model_id=model_id)

            # Check if any specifications exist
            if not specifications.exists():
                return JsonResponse({"success": False, "message": "No specifications found for this model."})

            # Delete all specifications for the model
            specifications.delete()
            redirect('customAdmin:specification')
            return JsonResponse({"success": True, "message": "Specifications deleted successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    redirect('customAdmin:specification')

    return JsonResponse({"success": False, "message": "Invalid request method."})


   


def get_models_by_brand(request):
    """Fetch models based on the selected brand."""
    brand_id = request.GET.get('brand_id')  # Get brand_id from the request
    if brand_id:
        models = Model.objects.filter(brand_id=brand_id).values('id', 'name')  # Fetch models related to the brand
        return JsonResponse({'models': list(models)})  # Convert queryset to a list and return as JSON
    return JsonResponse({'models': []})
   

def adminsettings(request):
    return render(request, 'adminsettings.html')
    
