from dj_rest_auth.registration.views import ConfirmEmailView
from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from sparepal.companies.api.views import AddressViewSet
from sparepal.companies.api.views import CompanyViewSet
from sparepal.companies.api.views import GetChoicesAPIView
from sparepal.companies.api.views import ManagerViewSet
from sparepal.users.api.views import GoogleLogin
from sparepal.users.api.views import ProfileDetailsAPIView
from sparepal.users.api.views import UserRedirectView

# Use DefaultRouter in debug mode for the browsable API; otherwise, use SimpleRouter
router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# Register users-related viewsets


# Register company-related viewsets
# Register companies root-level router
router.register(r"companies", CompanyViewSet, basename="companies")

# Create nested routers for `Address` and `Manager`
companies_router = routers.NestedDefaultRouter(router, "companies", lookup="company")

companies_router.register(r"addresses", AddressViewSet, basename="addresses")
companies_router.register(r"managers", ManagerViewSet, basename="managers")

# Base urlpatterns
urlpatterns = router.urls + companies_router.urls

# Non-viewset URLs for users
urlpatterns += [
    # Registration and email confirmation
    path(
        "auth/registration/account-confirm-email/<str:key>/",
        ConfirmEmailView.as_view(),
    ),  # Needs to be defined before the registration path
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    # Email verification
    path(
        "auth/account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    # Password reset
    path(
        "auth/password/reset/confirm/<slug:uidb64>/<slug:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Profile-related views
    path("profile/", ProfileDetailsAPIView.as_view(), name="profile-detail"),
    # Social login
    path("auth/google/", GoogleLogin.as_view(), name="google_login"),
    path("auth/~redirect/", view=UserRedirectView.as_view(), name="redirect"),
]

# Non-viewset URLs for company
urlpatterns += [
    path("companies/choices/", GetChoicesAPIView.as_view(), name="get_choices"),
]
