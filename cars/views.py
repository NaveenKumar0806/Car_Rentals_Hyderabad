from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Car


def car_list_view(request):
    qs = Car.objects.filter(is_active=True).select_related("category")
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    fuel = request.GET.get("fuel", "")
    transmission = request.GET.get("transmission", "")
    seats = request.GET.get("seats", "")
    max_price = request.GET.get("max_price", "")
    available_only = request.GET.get("available") == "on"
    sort = request.GET.get("sort", "")

    if q:
        qs = qs.filter(Q(brand__icontains=q) | Q(model__icontains=q))
    if category in ("regular", "luxury"):
        qs = qs.filter(category__name=category)
    if fuel:
        qs = qs.filter(fuel_type=fuel)
    if transmission:
        qs = qs.filter(transmission=transmission)
    if seats:
        try:
            qs = qs.filter(seating_capacity=int(seats))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(daily_price__lte=max_price)
        except ValueError:
            pass
    if available_only:
        qs = qs.filter(is_available=True)
    if sort == "price_asc":
        qs = qs.order_by("daily_price")
    elif sort == "price_desc":
        qs = qs.order_by("-daily_price")

    regular_cars = qs.filter(category__name="regular") if not category else (qs if category == "regular" else Car.objects.none())
    luxury_cars = qs.filter(category__name="luxury") if not category else (qs if category == "luxury" else Car.objects.none())
    # When filters narrow the qs, regular/luxury split above already reflects filters.
    context = {
        "cars": qs,
        "regular_cars": regular_cars,
        "luxury_cars": luxury_cars,
        "filters": request.GET,
    }
    return render(request, "cars/list.html", context)


def car_detail_view(request, pk):
    car = get_object_or_404(Car.objects.select_related("category").prefetch_related("images"), pk=pk, is_active=True)
    related = Car.objects.filter(category=car.category, is_active=True).exclude(pk=car.pk)[:4]
    return render(request, "cars/detail.html", {"car": car, "related": related})
