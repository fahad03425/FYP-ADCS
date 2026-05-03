from django.db import models
from django.utils.text import slugify
import uuid, random


# Generate unique integer IDs
def generate_unique_id():
    return random.randint(100000, 999999)


# Category Model
class Category(models.Model):
    category_id = models.IntegerField(default=generate_unique_id, unique=True, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Brand Model
class Brand(models.Model):
    brand_id = models.IntegerField(default=generate_unique_id, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="brands")
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('category', 'name')  # Prevent duplicate brand names in the same category
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Category: {self.category.name})"


# Model Model
class Model(models.Model):  # Consider renaming this class to avoid conflicts with `django.db.models.Model`
    model_id = models.IntegerField(default=generate_unique_id, unique=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="models")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('brand', 'name')  # Prevent duplicate model names in the same brand
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Brand: {self.brand.name}, Category: {self.category.name})"
    


class Specification(models.Model):
    specification_id = models.IntegerField(default=generate_unique_id, primary_key=True, unique=True, editable=False)
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="specifications")  
    ram = models.CharField(max_length=50)  
    storage = models.CharField(max_length=50)  
    battery = models.CharField(max_length=50)  
    sim_type = models.CharField(max_length=50)  
    e_sim = models.CharField(max_length=50, default="yes")  

    class Meta:
        verbose_name_plural = "Specifications"
        ordering = ['model__name', 'ram']

    def save(self, *args, **kwargs):
        # Optionally populate `model_name` and `brand_name` automatically
        if self.model:
            self.model_name = self.model.name
            self.brand_name = self.model.brand.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.model.name} - {self.ram}/{self.storage}"