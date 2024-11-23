from dj_rest_auth.registration.views import ConfirmEmailView
from dj_rest_auth.registration.views import VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView
from django.urls import include
from django.urls import path

from sparepal.users.api.views import GoogleLogin
from sparepal.users.api.views import ProfileDetailsAPIView
from sparepal.users.api.views import UserRedirectView

# Non-viewset URLs for users
urlpatterns = [
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
    path("~redirect/", view=UserRedirectView.as_view(), name="redirect"),
]
