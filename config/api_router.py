from dj_rest_auth.registration.views import ConfirmEmailView
from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from sparepal.companies.api.views import CompanyDetailAddressViewSet
from sparepal.companies.api.views import CompanyManagerDetailViewSet
from sparepal.companies.api.views import CompanyViewSet
from sparepal.companies.api.views import GetChoicesAPIView
from sparepal.users.api.views import GoogleLogin
from sparepal.users.api.views import ProfileDetailsAPIView
from sparepal.users.api.views import UserRedirectView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# Register users-related viewsets


# Register company-related viewsets
router.register(r"companies", CompanyViewSet)
router.register(r"company-detail-address", CompanyDetailAddressViewSet)
router.register(r"company-manager-detail", CompanyManagerDetailViewSet)


# Base urlpatterns
urlpatterns = router.urls

# Non-viewset URLs for users
urlpatterns += [
    # Registration and email confirmation
    path(
        "registration/account-confirm-email/<str:key>/",
        ConfirmEmailView.as_view(),
    ),  # Needs to be defined before the registration path
    path("", include("dj_rest_auth.urls")),
    path("registration/", include("dj_rest_auth.registration.urls")),
    # Email verification
    path(
        "account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    # Password reset
    path(
        "password/reset/confirm/<slug:uidb64>/<slug:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Profile-related views
    path("profile/", ProfileDetailsAPIView.as_view(), name="profile-detail"),
    # Social login
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("~redirect/", view=UserRedirectView.as_view(), name="redirect"),
]

# Non-viewset URLs for company
urlpatterns += [
    path("choices/", GetChoicesAPIView.as_view(), name="get_choices"),
]
