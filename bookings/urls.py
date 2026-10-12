from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_list_view, name="list"),
    path("book/<int:car_id>/", views.booking_create_view, name="create"),
    path("confirmation/<str:reference>/", views.booking_confirmation_view, name="confirmation"),
    path("cancel/<str:reference>/", views.booking_cancel_view, name="cancel"),
]
