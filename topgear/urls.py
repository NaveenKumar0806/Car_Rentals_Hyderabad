from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "TopGear Administration"
admin.site.site_title = "TopGear Admin"
admin.site.index_title = "Manage cars, bookings, customers & offers"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("accounts/", include("accounts.urls")),
    path("cars/", include("cars.urls")),
    path("bookings/", include("bookings.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
