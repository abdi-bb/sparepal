from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser
from .models import Profile

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Define the fields to display in the admin interface
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_supplier",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_supplier", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    # Define the form for creating and changing users
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_supplier",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_supplier",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    # Ensure that the email field is used as the unique identifier
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ("user", "avatar", "bio", "activeness", "created_at")
    search_fields = ("user__email",)
    ordering = ("-created_at",)


# Register the CustomUser and Profile models in the admin interface
