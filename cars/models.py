from django.core.validators import FileExtensionValidator
from django.db import models


class CarCategory(models.Model):
    REGULAR = "regular"
    LUXURY = "luxury"
    CATEGORY_CHOICES = [(REGULAR, "Regular"), (LUXURY, "Luxury")]

    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Car categories"

    def __str__(self):
        return self.get_name_display()


class Car(models.Model):
    FUEL_CHOICES = [
        ("petrol", "Petrol"),
        ("diesel", "Diesel"),
        ("cng", "CNG"),
        ("electric", "Electric"),
        ("hybrid", "Hybrid"),
    ]
    TRANSMISSION_CHOICES = [("manual", "Manual"), ("automatic", "Automatic")]

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    category = models.ForeignKey(CarCategory, on_delete=models.PROTECT, related_name="cars")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    seating_capacity = models.PositiveSmallIntegerField()
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    features = models.TextField(blank=True, help_text="Comma or newline separated features.")
    rental_terms = models.TextField(blank=True)
    pickup_info = models.TextField(blank=True, default="Pickup & drop: Hyderabad (Madhapur hub), 24x7 with prior booking.")
    image = models.ImageField(
        upload_to="cars/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    image_url = models.URLField(blank=True, help_text="Optional external image URL used when no upload exists.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["daily_price", "brand", "model"]
        constraints = [
            models.CheckConstraint(check=models.Q(daily_price__gte=0), name="car_price_non_negative"),
            models.CheckConstraint(check=models.Q(seating_capacity__gte=1), name="car_seats_positive"),
        ]

    def __str__(self):
        return f"{self.brand} {self.model}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None

    def feature_list(self):
        if not self.features:
            return []
        parts = [p.strip(" •-\t") for p in self.features.replace("\n", ",").split(",")]
        return [p for p in parts if p]


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="cars/gallery/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    image_url = models.URLField(blank=True)
    caption = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.car}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or None
