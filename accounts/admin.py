from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import CustomerProfile


class ProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "email", "get_full_name", "is_active", "date_joined")
    search_fields = ("username", "email", "profile__full_name", "profile__mobile_number")

    def get_full_name(self, obj):
        return getattr(obj.profile, "full_name", "") if hasattr(obj, "profile") else ""
    get_full_name.short_description = "Full name"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(CustomerProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "mobile_number", "created_at")
    search_fields = ("full_name", "mobile_number", "user__username", "user__email")
