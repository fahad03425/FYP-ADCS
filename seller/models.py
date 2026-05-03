from django.db import models
from marketplace.models import CustomUser  # Import the CustomUser model from marketplace app
from django.conf import settings
from django.utils import timezone
import random, os

# Create your models here.

class Sale(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale on {self.date} - PKR {self.amount}"
    
    
    
#                                             Shop Registration
    
def generate_shop_id():
    return random.randint(100000, 999999)
    
class ShopRegistration(models.Model):
    shopID = models.IntegerField(default=generate_shop_id)
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="shops"
     )
    shopname = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.TextField(max_length=100)
    location = models.CharField(max_length=255)
    creation_date = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return self.shopname
    
# ShopDetail Model
class ShopDetail(models.Model):
    SDid = models.AutoField(primary_key=True)
    fk_ShopID = models.OneToOneField(ShopRegistration, on_delete=models.CASCADE, related_name='shop_detail')
    shop_open = models.DateTimeField(null=True, blank=True)
    shop_close = models.DateTimeField(null=True, blank=True)
    holiday_mode = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    policy = models.TextField(max_length=1000, null=True, blank=True)
    image = models.ImageField(upload_to='shop_images/', null=True, blank=False)

    def delete(self, *args, **kwargs):
        # Delete the image file when the model instance is deleted
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Details for {self.fk_ShopID.shopname}"
    

#addProduct Model
    
class addProduct(models.Model):
    productID = models.AutoField(primary_key=True)
    fk_ShopID = models.ForeignKey(ShopRegistration, on_delete=models.CASCADE, related_name='addproduct')
    brand1 = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    imei = models.CharField(max_length=255)
    condition = models.CharField(max_length=255)
    colors = models.CharField(max_length=255)
    color2 = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    seller_sku = models.CharField(max_length=255)
    exchange = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    


def __str__(self):
    return f"{self.brand1} {self.model}"
    
#productImage Model
class productImage(models.Model):
        productImageID = models.AutoField(primary_key=True)
        fk_addProduct = models.ForeignKey(addProduct, on_delete=models.CASCADE, related_name='images')
        image = models.ImageField(upload_to='productimages/', null=True, blank=False)
        last_updated = models.DateTimeField(auto_now=True)
        
        def delete(self, *args, **kwargs):
            # Delete the image file when the model instance is deleted
            if self.image:
                if os.path.isfile(self.image.path):
                    os.remove(self.image.path)
            super().delete(*args, **kwargs)

        def __str__(self):
            return f"Product Image for {self.fk_addProduct.productID}"


class BookingOrder(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="booking_orders")
    product = models.ForeignKey(addProduct, on_delete=models.CASCADE,related_name="booking_orders")
    shop = models.ForeignKey(ShopRegistration, on_delete=models.CASCADE,related_name="booking_orders")
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    sold = models.BooleanField(default=False)
    booking_date = models.DateTimeField(auto_now_add=True)
    user_phone = models.CharField(max_length=15)
    cnic = models.CharField(max_length=15, null=True, blank=True)
    imei = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BookingOrder {self.id} for {self.product} by {self.user}"

    class Meta:
        verbose_name = "Booking/Order"
        verbose_name_plural = "Bookings/Orders"
