from django.urls import path
from . import views

app_name = "cars"

urlpatterns = [
    path("", views.car_list_view, name="list"),
    path("<int:pk>/", views.car_detail_view, name="detail"),
]
