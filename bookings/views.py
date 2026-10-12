from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from bookings.forms import BookingForm
from bookings.models import Booking
from cars.models import Car


@login_required
def booking_create_view(request, car_id):
    car = get_object_or_404(Car, pk=car_id, is_active=True)
    if not car.is_available:
        messages.error(request, "This car is currently unavailable.")
        return redirect("cars:detail", pk=car.pk)
    estimate = None
    if request.method == "POST":
        form = BookingForm(request.POST, car=car, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car
            booking.offer = getattr(form, "resolved_offer", None)
            booking.promo_code_used = (form.cleaned_data.get("promo_code") or "").strip().upper()
            try:
                booking.full_clean(exclude=["reference"])
            except ValidationError as e:
                form.add_error(None, e)
            else:
                booking.save()
                messages.success(request, f"Booking {booking.reference} created! {booking.payment_status}.")
                return redirect("bookings:confirmation", reference=booking.reference)
        # live estimate preview on error path
        try:
            tmp = Booking(
                user=request.user, car=car,
                pickup_datetime=form.cleaned_data.get("pickup_datetime") if form.is_bound else None,
                return_datetime=form.cleaned_data.get("return_datetime") if form.is_bound else None,
                offer=getattr(form, "resolved_offer", None),
            )
            if tmp.pickup_datetime and tmp.return_datetime and tmp.return_datetime > tmp.pickup_datetime:
                tmp.rental_days, tmp.base_amount, tmp.discount_amount, tmp.total_amount = tmp.calculate_amounts()
                estimate = tmp
        except Exception:
            estimate = None
    else:
        form = BookingForm(car=car, user=request.user)
    return render(request, "bookings/create.html", {"car": car, "form": form, "estimate": estimate})


@login_required
def booking_confirmation_view(request, reference):
    booking = get_object_or_404(Booking.objects.select_related("car", "car__category"), reference=reference, user=request.user)
    return render(request, "bookings/confirmation.html", {"booking": booking})


@login_required
def booking_list_view(request):
    bookings = Booking.objects.filter(user=request.user).select_related("car").order_by("-created_at")
    return render(request, "bookings/list.html", {"bookings": bookings})


@login_required
def booking_cancel_view(request, reference):
    booking = get_object_or_404(Booking, reference=reference, user=request.user)
    if request.method == "POST":
        if booking.status in ("pending", "confirmed"):
            booking.status = "cancelled"
            booking.save()
            messages.success(request, f"Booking {booking.reference} cancelled.")
        else:
            messages.error(request, "Only pending/confirmed bookings can be cancelled.")
        return redirect("accounts:dashboard")
    return render(request, "bookings/cancel_confirm.html", {"booking": booking})
