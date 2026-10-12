from django.contrib import admin
from .models import Booking, PromotionalOffer


@admin.register(PromotionalOffer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "promo_code", "discount_percent", "min_days", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("title", "promo_code")
    list_editable = ("is_active",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "car", "pickup_datetime", "return_datetime", "rental_days", "total_amount", "status", "payment_status")
    list_filter = ("status", "payment_status", "pickup_datetime", "car__category")
    search_fields = ("reference", "user__username", "user__email", "car__brand", "car__model")
    readonly_fields = ("reference", "rental_days", "base_amount", "discount_amount", "total_amount", "created_at", "updated_at")
    actions = ["mark_confirmed", "mark_cancelled", "mark_completed"]

    @admin.action(description="Mark selected as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status="confirmed")

    @admin.action(description="Mark selected as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status="cancelled")

    @admin.action(description="Mark selected as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status="completed")
