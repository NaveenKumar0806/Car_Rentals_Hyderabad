from django import forms
from django.utils import timezone

from bookings.models import Booking, PromotionalOffer


class BookingForm(forms.ModelForm):
    promo_code = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Promo code (optional)"}))

    class Meta:
        model = Booking
        fields = ("pickup_datetime", "return_datetime", "pickup_location", "return_location", "licence_number")
        widgets = {
            "pickup_datetime": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "return_datetime": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "pickup_location": forms.TextInput(attrs={"class": "form-control"}),
            "return_location": forms.TextInput(attrs={"class": "form-control"}),
            "licence_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Driving licence number"}),
        }

    def __init__(self, *args, car=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.car = car
        self.user = user

    def clean(self):
        cleaned = super().clean()
        pickup = cleaned.get("pickup_datetime")
        ret = cleaned.get("return_datetime")
        if pickup and ret and ret <= pickup:
            raise forms.ValidationError("Return date/time must be after pickup date/time.")
        if pickup and pickup < timezone.now() - timezone.timedelta(minutes=5):
            raise forms.ValidationError("Pickup time cannot be in the past.")
        # Resolve promo code
        code = (cleaned.get("promo_code") or "").strip()
        self.resolved_offer = None
        if code:
            try:
                offer = PromotionalOffer.objects.get(promo_code__iexact=code)
                if not offer.is_valid_on(timezone.now().date()):
                    raise forms.ValidationError("This promo code is expired or inactive.")
                self.resolved_offer = offer
            except PromotionalOffer.DoesNotExist:
                raise forms.ValidationError("Invalid promo code.")
        return cleaned
