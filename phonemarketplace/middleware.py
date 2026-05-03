# phonemarketplace/middleware.py

from django.shortcuts import redirect
from django.urls import reverse

class SellerLoginRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for a seller page and if the user is authenticated
        if request.path.startswith('/seller/') and not request.user.is_authenticated:
            # Redirect to 'frontpage' with next URL parameter
            login_url = f"{reverse('frontpage')}?next={request.path}"
            return redirect(login_url)
        
        # Otherwise, proceed as normal
        response = self.get_response(request)
        return response
