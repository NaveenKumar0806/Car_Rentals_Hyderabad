from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bookings.models import Booking
from .forms import LoginForm, ProfileUpdateForm, RegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("pages:home")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to TopGear! Your account has been created.")
            return redirect("pages:home")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("pages:home")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Logged in successfully.")
            return redirect(request.GET.get("next") or "pages:home")
        messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("pages:home")
    logout(request)
    return redirect("pages:home")


@login_required
def dashboard_view(request):
    profile = getattr(request.user, "profile", None)
    bookings = Booking.objects.filter(user=request.user).select_related("car", "car__category").order_by("-created_at")
    upcoming = bookings.filter(status__in=["pending", "confirmed"])
    history = bookings.exclude(status__in=["pending", "confirmed"])
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile, initial={"email": request.user.email})
        if form.is_valid():
            form.save()
            email = form.cleaned_data["email"]
            if email != request.user.email:
                request.user.email = email
                request.user.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:dashboard")
    else:
        form = ProfileUpdateForm(instance=profile, initial={"email": request.user.email})
    return render(
        request,
        "accounts/dashboard.html",
        {"profile": profile, "form": form, "upcoming": upcoming, "history": history},
    )
