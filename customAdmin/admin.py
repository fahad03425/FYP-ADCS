from django.contrib import admin
from .models import Category , Brand , Model, Specification
# Admin view for Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_id')  
    search_fields = ('name', 'slug') 
    prepopulated_fields = {'slug': ('name',)}  


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category_id')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand_id', 'category_id')
    list_filter = ('category', 'brand')
    search_fields = ('name',)
    
# Admin view for Specification model
@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('specification_id', 'model', 'ram', 'storage', 'battery', 'sim_type', 'e_sim')  # Display key fields
    list_filter = ('sim_type', 'e_sim')  # Filters for specific attributes
    search_fields = ('model__name', 'ram', 'storage')  # Enable search by model name, RAM, and storage
    ordering = ['model__name']  # Default order by model name
