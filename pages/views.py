from django.shortcuts import render
from django.utils import timezone

from bookings.models import PromotionalOffer
from cars.models import Car


def home_view(request):
    offers = PromotionalOffer.objects.filter(is_active=True, valid_from__lte=timezone.now().date(), valid_to__gte=timezone.now().date())[:6]
    popular = Car.objects.filter(is_active=True, is_available=True, is_popular=True).select_related("category")[:8]
    if not popular.exists():
        popular = Car.objects.filter(is_active=True, is_available=True).select_related("category")[:8]
    return render(request, "pages/home.html", {"offers": offers, "popular": popular})


def about_view(request):
    return render(request, "pages/about.html")
