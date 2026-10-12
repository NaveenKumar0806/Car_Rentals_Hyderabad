from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=150)
    mobile_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?\d{10,15}$", "Enter a valid mobile number.")],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.email or self.user.username})"
