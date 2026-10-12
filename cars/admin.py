from django.contrib import admin
from .models import Car, CarCategory, CarImage


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "category", "transmission", "fuel_type", "seating_capacity", "daily_price", "is_available", "is_active", "is_popular")
    list_filter = ("category", "transmission", "fuel_type", "is_available", "is_active", "is_popular")
    search_fields = ("brand", "model")
    list_editable = ("daily_price", "is_available", "is_active", "is_popular")
    inlines = [CarImageInline]


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ("car", "caption", "created_at")
