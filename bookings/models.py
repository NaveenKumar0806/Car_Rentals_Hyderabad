import uuid
from decimal import Decimal
from math import ceil

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from cars.models import Car


def generate_booking_reference():
    return "TG-" + uuid.uuid4().hex[:8].upper()


class PromotionalOffer(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    promo_code = models.CharField(max_length=30, unique=True, blank=True, help_text="Leave blank for auto offers.")
    min_days = models.PositiveIntegerField(default=1)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="0 means no cap.")
    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)
    applicable_categories = models.CharField(
        max_length=50, default="both", help_text="regular, luxury or both"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_active", "valid_to"]

    def __str__(self):
        return f"{self.title} ({self.promo_code or 'auto'})"

    def clean(self):
        if self.valid_to < self.valid_from:
            raise ValidationError("Offer validity end must be on/after start.")
        if not (0 <= self.discount_percent <= 100):
            raise ValidationError("Discount percent must be between 0 and 100.")

    def is_valid_on(self, date=None):
        date = date or timezone.now().date()
        return self.is_active and self.valid_from <= date <= self.valid_to


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    PAYMENT_CHOICES = [
        ("awaiting", "Awaiting payment"),
        ("pickup", "Payment on pickup"),
        ("paid", "Paid"),
    ]

    reference = models.CharField(max_length=20, unique=True, default=generate_booking_reference, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name="bookings")
    pickup_datetime = models.DateTimeField()
    return_datetime = models.DateTimeField()
    pickup_location = models.CharField(max_length=200, default="TopGear Hub, Madhapur, Hyderabad")
    return_location = models.CharField(max_length=200, default="TopGear Hub, Madhapur, Hyderabad")
    licence_number = models.CharField(max_length=50, blank=True)
    offer = models.ForeignKey(PromotionalOffer, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    promo_code_used = models.CharField(max_length=30, blank=True)
    rental_days = models.PositiveIntegerField(default=1)
    base_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="pickup")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.car} ({self.user})"

    def clean(self):
        if self.return_datetime <= self.pickup_datetime:
            raise ValidationError("Return date/time must be after pickup date/time.")
        if self.pickup_datetime < timezone.now() - timezone.timedelta(minutes=5):
            raise ValidationError("Pickup time cannot be in the past.")
        # Overlapping check for pending/confirmed bookings of same car
        overlapping = Booking.objects.filter(
            car=self.car,
            status__in=["pending", "confirmed"],
            pickup_datetime__lt=self.return_datetime,
            return_datetime__gt=self.pickup_datetime,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("This car is already booked for the selected period.")

    @staticmethod
    def compute_days(pickup, dropoff):
        seconds = (dropoff - pickup).total_seconds()
        if seconds <= 0:
            return 0
        return max(1, ceil(seconds / 86400))

    def calculate_amounts(self, offer=None):
        days = self.compute_days(self.pickup_datetime, self.return_datetime)
        base = Decimal(self.car.daily_price) * days
        discount = Decimal("0")
        applied = offer or self.offer
        if applied and applied.is_valid_on(timezone.now().date()):
            cat = self.car.category.name
            if applied.applicable_categories in ("both", cat) and days >= applied.min_days:
                discount = base * (Decimal(applied.discount_percent) / Decimal("100"))
                if applied.max_discount and applied.max_discount > 0:
                    discount = min(discount, applied.max_discount)
        total = base - discount
        return days, base.quantize(Decimal("0.01")), discount.quantize(Decimal("0.01")), total.quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        if self.pickup_datetime and self.return_datetime and self.car_id:
            self.rental_days, self.base_amount, self.discount_amount, self.total_amount = self.calculate_amounts()
        super().save(*args, **kwargs)
