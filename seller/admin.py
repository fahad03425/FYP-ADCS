from django.contrib import admin
from .models import  ShopRegistration, ShopDetail, addProduct, productImage, BookingOrder

# Register your models here.
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount')  # This will display these fields in the list view
    list_filter = ('date',)  # Allows filtering by date
    search_fields = ('date',)  # Allows searching 

@admin.register(ShopRegistration)
class ShopRegistrationAdmin(admin.ModelAdmin):
   # Update list_display fields to match model fields
    list_display = ('shopID', 'user', 'shopname', 'city', 'area', 'location', 'isActive', 'creation_date', 'last_update')
    # Update search fields and list filters to match model fields
    search_fields = ('shopname', 'city', 'area', 'user__username')  # Assuming 'user' is a ForeignKey to a User model
    list_filter = ('city', 'isActive', 'creation_date')

    # Specify fields in detail view, and correct field names for readonly_fields
    fields = ('shopID', 'user', 'shopname', 'city', 'area', 'location', 'creation_date', 'last_update', 'isActive')
    readonly_fields = ('creation_date', 'last_update')  # Ensure these fields exist in the model

# ShopDetail Admin
@admin.register(ShopDetail)
class ShopDetailAdmin(admin.ModelAdmin):
    list_display = ('fk_ShopID', 'shop_open', 'shop_close', 'holiday_mode', 'last_updated', 'image','policy')
    list_filter = ('holiday_mode', 'last_updated')
    search_fields = ('fk_ShopID__shopname', 'fk_ShopID__shopID')
    ordering = ('-last_updated',)
    readonly_fields = ('last_updated',)

class productImageInline(admin.TabularInline):
    model = productImage
    extra = 1  # Number of empty image fields to display
    fields = ['image']  # Fields displayed in the inline section
    max_num = 3  # Limit to 3 images per product
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"

@admin.register(addProduct)
class addProductAdmin(admin.ModelAdmin):
    list_display = (
        'productID', 'get_shop_name', 'brand1', 'model', 'imei', 'condition', 
        'colors', 'color2', 'description', 'price', 'stock', 'seller_sku', 
        'exchange','isActive', 'creation_date', 'last_updated'
    )  # Display all fields

    list_filter = ('brand1', 'condition', 'exchange')  # Filters on the right
    search_fields = ('brand1', 'model', 'imei', 'description')  # Searchable fields
    readonly_fields = ('creation_date', 'last_updated')  # Timestamps read-only

    # Organize fields into collapsible sections
    fieldsets = (
        ("Basic Information", {
            'fields': ('fk_ShopID', 'brand1', 'model', 'imei', 'condition'),
        }),
        ("Details", {
            'fields': ('colors', 'color2', 'description', 'price', 'stock', 'seller_sku', 'exchange'),
        }),
        ("Timestamps", {
            'fields': ('creation_date', 'last_updated'),
        }),
    )

    def get_shop_name(self, obj):
        """Fetch the shop name from the related ShopRegistration model."""
        return obj.fk_ShopID.shopname  # Replace `shop_name` with the actual field in ShopRegistration
    get_shop_name.short_description = 'Shop Name'


@admin.register(productImage)
class productImageAdmin(admin.ModelAdmin):
    list_display = ('productImageID', 'fk_addProduct', 'image', 'last_updated')  # Fields to display in the image list
    list_filter = ('last_updated',)  # Filter by update time
    search_fields = ('fk_addProduct__brand', 'fk_addProduct__model') 

@admin.register(BookingOrder)
class BookingOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'shop', 'status', 'created_at', 'cnic', 'imei')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__model', 'shop__shopname', 'cnic', 'imei')
